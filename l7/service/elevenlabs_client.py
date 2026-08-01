"""ElevenLabs TTS client.

Hedra bills its own text_to_speech step on top of the video render, and that
step is the expensive half of a talking head. Synthesising the narration here
and handing Hedra a finished audio asset keeps the lip-sync and drops the TTS
charge.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import requests

from .retry import with_retry

LOGGER = logging.getLogger("l7.elevenlabs")

DEFAULT_BASE_URL = "https://api.elevenlabs.io/v1"
DEFAULT_TIMEOUT = (10.0, 300.0)

# ElevenLabs v3 exposes stability as three presets rather than a slider.
# Names are what the UI shows; values are what the API takes.
STABILITY_PRESETS = {"creative": 0.0, "natural": 0.5, "robust": 1.0}


class ElevenLabsError(RuntimeError):
    pass


def _mask_key(key: str) -> str:
    if len(key) <= 12:
        return "sk_***"
    return f"{key[:6]}…{key[-4:]}"


def resolve_stability(value: Any) -> float | None:
    """Accept either a preset name ('robust') or a raw 0-1 number."""
    if value is None:
        return None
    if isinstance(value, str):
        key = value.strip().lower()
        if key not in STABILITY_PRESETS:
            raise ElevenLabsError(
                f"unknown stability preset {value!r}; "
                f"expected one of {sorted(STABILITY_PRESETS)} or a number 0-1"
            )
        return STABILITY_PRESETS[key]
    return float(value)


class ElevenLabsClient:
    # Checked in order when ELEVENLABS_API_KEY is not exported. Keep these
    # OUT of git — a leaked key is a billable secret.
    _KEY_FILES = ("~/.elevenlabs_key", ".elevenlabs_key")

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: tuple[float, float] = DEFAULT_TIMEOUT,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        env_key = os.environ.get("ELEVENLABS_API_KEY")
        file_key = self._key_from_file()
        self.api_key = api_key or env_key or file_key
        if not self.api_key:
            raise ElevenLabsError(
                "ELEVENLABS_API_KEY not found. Either export it:\n"
                "  export ELEVENLABS_API_KEY=sk_...\n"
                "or store it once so every new shell picks it up:\n"
                f"  echo 'sk_...' > {self._KEY_FILES[0]} && "
                f"chmod 600 {self._KEY_FILES[0]}"
            )
        source = ("argument" if api_key
                  else "ELEVENLABS_API_KEY env var" if env_key
                  else "key file")
        LOGGER.info("api_key_source",
                    extra={"source": source, "key": _mask_key(self.api_key)})
        if env_key and file_key and env_key != file_key:
            LOGGER.warning(
                "api_key_conflict",
                extra={"note": "ELEVENLABS_API_KEY and the key file hold "
                               "DIFFERENT keys; the env var wins. Run "
                               "`unset ELEVENLABS_API_KEY` to use the file.",
                       "env_key": _mask_key(env_key),
                       "file_key": _mask_key(file_key)})
        self.session = session or requests.Session()

    @classmethod
    def _key_from_file(cls) -> str | None:
        for candidate in cls._KEY_FILES:
            try:
                key = Path(candidate).expanduser().read_text(
                    encoding="utf-8").strip()
            except OSError:
                continue
            if key:
                return key
        return None

    # ------------------------------------------------------------------ tts
    # voice_settings fields are model-dependent: eleven_v3 rejects `speed`,
    # older models reject nothing we send. Rather than hard-code a matrix that
    # goes stale, drop the field the API complains about and retry.
    _OPTIONAL_SETTINGS = ("speed", "style", "use_speaker_boost",
                          "similarity_boost", "stability")

    def synthesize(
        self,
        *,
        text: str,
        voice_id: str,
        model_id: str = "eleven_multilingual_v2",
        stability: float | None = None,
        similarity_boost: float | None = None,
        style: float | None = None,
        speed: float | None = None,
        use_speaker_boost: bool | None = None,
        output_format: str = "mp3_44100_128",
        language_code: str | None = None,
    ) -> bytes:
        """POST /text-to-speech/{voice_id} — returns the audio bytes."""
        settings: dict[str, Any] = {}
        if stability is not None:
            settings["stability"] = stability
        if similarity_boost is not None:
            settings["similarity_boost"] = similarity_boost
        if style is not None:
            settings["style"] = style
        if speed is not None:
            settings["speed"] = speed
        if use_speaker_boost is not None:
            settings["use_speaker_boost"] = use_speaker_boost

        dropped: list[str] = []
        while True:
            payload: dict[str, Any] = {"text": text, "model_id": model_id}
            if settings:
                payload["voice_settings"] = dict(settings)
            if language_code:
                payload["language_code"] = language_code

            LOGGER.info("tts_request",
                        extra={"voice_id": voice_id, "model_id": model_id,
                               "chars": len(text), "settings": dict(settings),
                               "output_format": output_format})
            resp = self._post(
                f"/text-to-speech/{voice_id}",
                json=payload,
                params={"output_format": output_format},
            )
            if 200 <= resp.status_code < 300:
                audio = resp.content
                if not audio:
                    raise ElevenLabsError(
                        "text-to-speech returned an empty body")
                if dropped:
                    LOGGER.warning(
                        "tts_settings_dropped",
                        extra={"dropped": dropped, "model_id": model_id,
                               "note": "model rejected these voice_settings; "
                                       "audio was produced without them"})
                LOGGER.info("tts_ok", extra={"bytes": len(audio)})
                return audio

            body = resp.text[:500] if resp.text else ""
            offender = self._rejected_setting(resp.status_code, body, settings)
            if offender is None:
                raise ElevenLabsError(
                    f"POST /text-to-speech/{voice_id} → "
                    f"{resp.status_code}: {body}"
                )
            # Retry without the field the API named, so a model/settings
            # mismatch degrades to working audio instead of no audio.
            settings.pop(offender)
            dropped.append(offender)
            LOGGER.warning("tts_retry_without_setting",
                           extra={"setting": offender,
                                  "status": resp.status_code,
                                  "err": body[:200]})

    def _rejected_setting(
        self, status: int, body: str, settings: dict[str, Any]
    ) -> str | None:
        """Name the voice_settings field this 4xx is complaining about."""
        if status not in (400, 422):
            return None
        lowered = body.lower()
        for field in self._OPTIONAL_SETTINGS:
            if field in settings and field in lowered:
                return field
        return None

    def _post(self, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self.base_url}{path}"
        headers = {"xi-api-key": self.api_key, "accept": "audio/mpeg"}

        def _do() -> requests.Response:
            return self.session.request(
                "POST", url, headers=headers, timeout=self.timeout, **kwargs
            )

        resp = with_retry(_do)
        LOGGER.info("elevenlabs_response",
                    extra={"path": path, "status": resp.status_code})
        return resp

    # ---------------------------------------------------------------- voices
    def list_voices(self) -> list[dict[str, Any]]:
        """GET /voices — used to confirm a voice_id belongs to this account."""
        url = f"{self.base_url}/voices"

        def _do() -> requests.Response:
            return self.session.request(
                "GET", url, headers={"xi-api-key": self.api_key},
                timeout=self.timeout,
            )

        resp = with_retry(_do)
        if not (200 <= resp.status_code < 300):
            raise ElevenLabsError(
                f"GET /voices → {resp.status_code}: {resp.text[:300]}")
        data = resp.json()
        voices = data.get("voices") if isinstance(data, dict) else data
        return voices if isinstance(voices, list) else []
