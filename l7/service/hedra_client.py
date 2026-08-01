"""Thin HTTP wrapper around Hedra API. Covers NR-F1-1..F1-3, F1-6, F1-10."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import requests

from .retry import with_retry

LOGGER = logging.getLogger("l7.hedra")

DEFAULT_BASE_URL = "https://api.hedra.com/web-app/public"
DEFAULT_TIMEOUT = (10.0, 120.0)  # (connect, read)


class HedraError(RuntimeError):
    pass


class HedraInsufficientBalance(HedraError):
    """402 from Hedra. No payload shape fixes this — only money does."""


def _mask_key(key: str) -> str:
    """Enough to tell two keys apart in a log, not enough to use one."""
    if len(key) <= 14:
        return "sk_hedra_***"
    return f"{key[:12]}…{key[-4:]}"


class HedraClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        timeout: tuple[float, float] = DEFAULT_TIMEOUT,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        env_key = os.environ.get("HEDRA_API_KEY")
        file_key = self._key_from_file()
        self.api_key = api_key or env_key or file_key
        if api_key:
            source = "argument"
        elif env_key:
            source = "HEDRA_API_KEY env var"
        else:
            source = "key file"
        if self.api_key:
            # Which key is in play, in the clear, every run. A stale exported
            # key silently shadowing a freshly written ~/.hedra_key cost a
            # whole debugging round once — never again without it being visible.
            LOGGER.info("api_key_source",
                        extra={"source": source,
                               "key": _mask_key(self.api_key)})
        if env_key and file_key and env_key != file_key:
            LOGGER.warning(
                "api_key_conflict",
                extra={"note": "HEDRA_API_KEY and the key file hold DIFFERENT "
                               "keys; the env var wins. Run "
                               "`unset HEDRA_API_KEY` to use the file.",
                       "env_key": _mask_key(env_key),
                       "file_key": _mask_key(file_key)})
        if not self.api_key:
            raise HedraError(
                "HEDRA_API_KEY not found. Either export it:\n"
                "  export HEDRA_API_KEY=sk_hedra_...\n"
                "or store it once so every new shell picks it up:\n"
                f"  echo 'sk_hedra_...' > {self._KEY_FILES[0]} && "
                f"chmod 600 {self._KEY_FILES[0]}"
            )
        self.session = session or requests.Session()

    # Checked in order when HEDRA_API_KEY is not exported. Keep these OUT of
    # git — a leaked key is a billable secret.
    _KEY_FILES = ("~/.hedra_key", ".hedra_key")

    @classmethod
    def _key_from_file(cls) -> str | None:
        for candidate in cls._KEY_FILES:
            path = Path(candidate).expanduser()
            try:
                key = path.read_text(encoding="utf-8").strip()
            except OSError:
                continue
            if key:
                cls._key_file_used = str(path)
                return key
        return None

    _key_file_used: str | None = None

    # ------------------------------------------------------------------ utils
    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = {"X-API-KEY": self.api_key}
        if extra:
            headers.update(extra)
        return headers

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
        files: dict | None = None,
        params: dict | None = None,
        stream: bool = False,
    ) -> requests.Response:
        url = f"{self.base_url}{path}" if path.startswith("/") else path
        LOGGER.info(
            "hedra_request",
            extra={"method": method, "path": path, "params": params},
        )

        def _do() -> requests.Response:
            return self.session.request(
                method,
                url,
                headers=self._headers(),
                json=json,
                files=files,
                params=params,
                timeout=self.timeout,
                stream=stream,
            )

        resp = with_retry(_do)
        LOGGER.info(
            "hedra_response",
            extra={"method": method, "path": path, "status": resp.status_code},
        )
        if not (200 <= resp.status_code < 300):
            body = resp.text[:500] if resp.text else ""
            msg = f"{method} {path} → {resp.status_code}: {body}"
            if resp.status_code == 402:
                raise HedraInsufficientBalance(msg)
            raise HedraError(msg)
        return resp

    # ----------------------------------------------------------------- models
    def list_models(self) -> list[dict[str, Any]]:
        """GET /models — list available AI models, returns raw list."""
        resp = self._request("GET", "/models")
        data = resp.json()
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("models", "items", "data"):
                if key in data and isinstance(data[key], list):
                    return data[key]
        raise HedraError(f"list_models: unexpected shape {type(data).__name__}")

    # Hedra has dozens of "video" models from many vendors (Kling, Veo, etc.).
    # The ones that drive a talking-head avatar from an image carry "Hedra",
    # "Avatar" or "Character" in their name. Search those first.
    _AVATAR_HINTS = ("hedra avatar", "hedra character", "character-3",
                     "hedra avatar 540", "avatar 540", "avatar")

    def resolve_video_model_id(
        self, *, name_hint: str = "Hedra Avatar 540p"
    ) -> str:
        """Find a Hedra avatar video model by name; fall back to the first
        model whose name contains 'hedra' or 'avatar'.

        Raises HedraError with the full model list if nothing matched —
        the user can then pass `--ai-model-id` explicitly.
        """
        models = self.list_models()
        all_names = [m.get("name") for m in models]
        LOGGER.info(
            "models_listed",
            extra={"count": len(models),
                   "names_head": all_names[:20]},
        )

        def model_id(m: dict) -> str:
            return str(m.get("id") or m.get("ai_model_id"))

        def is_video(m: dict) -> bool:
            t = (m.get("type") or m.get("model_type") or "").lower()
            return t == "" or t == "video"

        # 1) exact case-insensitive name match.
        for m in models:
            if m.get("name") and m["name"].lower() == name_hint.lower():
                return model_id(m)

        # 2) substring match in the user-provided hint.
        hint_lower = name_hint.lower()
        for m in models:
            if m.get("name") and hint_lower in m["name"].lower() and is_video(m):
                return model_id(m)

        # 3) Hedra-specific avatar keywords (in order of preference).
        for kw in self._AVATAR_HINTS:
            for m in models:
                if m.get("name") and kw in m["name"].lower() and is_video(m):
                    return model_id(m)

        raise HedraError(
            "resolve_video_model_id: no Hedra avatar model found. "
            f"Pass --ai-model-id explicitly. Available models ({len(models)}): "
            f"{all_names}"
        )

    # ---------------------------------------------------------------- billing
    def get_credits(self) -> dict[str, Any]:
        """GET /billing/credits — the balance the API actually debits.

        Hedra bills programmatic usage from a *segregated API wallet* that is
        separate from the subscription/Studio credits shown in the web UI.
        Per Hedra's OpenAPI schema (WorkspaceCreditUsage):
          api_usd_micros  — API wallet balance in micro-dollars; "only present
                            while the API wallet is enabled and funded; spent
                            exclusively by programmatic API usage"
          api_credits     — display view of the same wallet
        So `remaining` can look healthy while generations still 402 — check
        workspace_credit_pool[*].api_usd_micros to see the real API balance.
        """
        resp = self._request("GET", "/billing/credits")
        return resp.json()

    # ----------------------------------------------------------------- voices
    _VOICES_ATTEMPTS = (
        # (path, params) — covering known Hedra variants where user-owned
        # cloned voices live behind a query flag or a separate path.
        ("/voices", None),
        ("/voices", {"include_user_voices": "true"}),
        ("/voices", {"owner": "me"}),
        ("/voices", {"type": "cloned"}),
        ("/voices", {"is_public": "false"}),
        ("/voices/user", None),
        ("/user/voices", None),
        ("/account/voices", None),
        ("/me/voices", None),
    )

    @staticmethod
    def _extract_voices(data: Any) -> list[dict] | None:
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ("voices", "items", "data", "results"):
                if isinstance(data.get(key), list):
                    return data[key]
        return None

    def list_voices(self) -> list[dict[str, Any]]:
        """Aggregate voices from every endpoint we know Hedra might use.

        Returns a list of unique voices (deduped by id). Each item carries
        a `_source` key showing which path produced it.
        """
        seen: dict[str, dict] = {}
        for path, params in self._VOICES_ATTEMPTS:
            try:
                resp = self._request("GET", path, params=params)
            except HedraError as exc:
                LOGGER.info(
                    "voices_endpoint_skipped",
                    extra={"path": path, "params": params, "err": str(exc)[:80]},
                )
                continue
            voices = self._extract_voices(resp.json())
            if not voices:
                continue
            for v in voices:
                vid = str(v.get("id") or v.get("voice_id") or "")
                if not vid or vid in seen:
                    continue
                v["_source"] = f"{path}?{params}" if params else path
                seen[vid] = v
        if not seen:
            raise HedraError("list_voices: no voices returned by any endpoint")
        return list(seen.values())

    # Hedra preset voices expose "name"; user-cloned voices use "voice_name".
    _VOICE_NAME_KEYS = ("name", "voice_name", "display_name", "label", "title", "slug")

    def resolve_voice_id(self, *, name_hint: str = "aisala") -> str:
        """Find a voice by display name across multiple possible name keys."""
        voices = self.list_voices()
        sample_names = []
        for v in voices[:20]:
            for k in self._VOICE_NAME_KEYS:
                if v.get(k):
                    sample_names.append(f"{k}={v[k]}")
                    break
        LOGGER.info(
            "voices_listed",
            extra={"count": len(voices), "names_head": sample_names},
        )

        def voice_id(v: dict) -> str:
            return str(v.get("id") or v.get("voice_id"))

        hint_lower = name_hint.lower()
        # Two passes: exact match across all known name keys, then substring.
        for exact in (True, False):
            for v in voices:
                for key in self._VOICE_NAME_KEYS:
                    name = v.get(key)
                    if not name:
                        continue
                    name_lower = str(name).lower()
                    if exact and name_lower == hint_lower:
                        return voice_id(v)
                    if not exact and hint_lower in name_lower:
                        return voice_id(v)

        raise HedraError(
            f"resolve_voice_id: voice {name_hint!r} not found. "
            f"Pass --voice-id explicitly. Sample names ({len(voices)} voices): "
            f"{sample_names}"
        )

    # ----------------------------------------------------------------- assets
    def create_image_asset(self, name: str) -> str:
        """POST /assets — create image asset metadata, return asset_id.

        Some Hedra deployments accept `{"name": ..., "type": "image"}`;
        we send both common shapes for robustness.
        """
        payload = {"name": name, "type": "image"}
        resp = self._request("POST", "/assets", json=payload)
        data: dict[str, Any] = resp.json()
        asset_id = data.get("id") or data.get("asset_id")
        if not asset_id:
            raise HedraError(f"create_image_asset: no 'id' in response: {data}")
        return str(asset_id)

    def upload_asset_binary(self, asset_id: str, path: Path) -> None:
        """POST /assets/{id}/upload — multipart binary upload."""
        path = Path(path)
        with path.open("rb") as fh:
            files = {"file": (path.name, fh, "image/jpeg")}
            # NB: requests will set Content-Type with boundary on multipart.
            self._request(
                "POST",
                f"/assets/{asset_id}/upload",
                files=files,
            )

    # ------------------------------------------------------------------ audio
    # Hedra Avatar in the 2026 schema rejects inline text+voice with
    # "video generation without valid audio input". Audio must be pre-
    # generated as a separate asset and referenced by audio_id.
    # Hedra's discriminator tags (discovered via 422 from /generations):
    #   'video', 'text_to_speech', 'text_to_sound', 'image', 'image_to_image',
    #   'image_upscale', 'video_upscale', 'audio_isolation',
    #   'speech_to_speech', 'voice_clone', 'audio_from_video',
    #   'video_with_audio', 'video_to_video', 'motion_control'
    # For talking-head from text + voice clone, the right tag is
    # `video_with_audio` (single call). If Hedra rejects inline text+voice,
    # we fall back to `text_to_speech` → asset_id → `video`.
    # Hedra confirmed (via 422):
    #   "video_with_audio not supported, only video, image, and
    #    text_to_speech generations are supported at this time"
    # So talking-head requires the two-step:
    #   1) type=text_to_speech → audio asset id
    #   2) type=video with audio_id (+ start_keyframe_id)
    # Body shape for text_to_speech follows the same naming convention as
    # video_with_audio: <discriminator>_model_id + <discriminator>_inputs.
    # Discovered from a live Hedra web-app response payload (response):
    #   generated_audio_inputs: {
    #     text_prompt, voice_id, voice_name, ai_model_id, model_slug,
    #     stability, speed, language, ...
    #   }
    # So the canonical request is nested with `text_prompt` and the voice
    # settings live next to it. The flat variants below are kept as
    # fallbacks for older Hedra builds.
    _AUDIO_ATTEMPTS = (
        ("/generations", {
            "type": "text_to_speech",
            "generated_audio_inputs": {
                "text_prompt": "{text}",
                "voice_id": "{voice_id}",
            },
        }),
        ("/generations", {
            "type": "text_to_speech",
            "text_prompt": "{text}",
            "voice_id": "{voice_id}",
        }),
        ("/generations", {
            "type": "text_to_speech",
            "text": "{text}",
            "voice_id": "{voice_id}",
        }),
        ("/generations", {
            "type": "text_to_speech",
            "text_to_speech_model_id": "{model_id}",
            "generated_audio_inputs": {
                "text_prompt": "{text}",
                "voice_id": "{voice_id}",
            },
        }),
    )

    @staticmethod
    def _fill_template(tpl: Any, *, text: str, voice_id: str, model_id: str | None) -> Any:
        if isinstance(tpl, str):
            out = tpl.replace("{text}", text).replace("{voice_id}", voice_id)
            if model_id is not None:
                out = out.replace("{model_id}", model_id)
            return out
        if isinstance(tpl, dict):
            return {
                k: HedraClient._fill_template(v, text=text, voice_id=voice_id, model_id=model_id)
                for k, v in tpl.items()
            }
        return tpl

    @staticmethod
    def _inject_voice_settings(payload: dict, speed: float,
                               stability: float | None) -> None:
        """Add TTS voice settings (speed, stability) to a text_to_speech
        payload, in place.

        Hedra reads `speed` and `stability` directly from
        `generated_audio_inputs` (confirmed from a live web-app payload).
        For the flat fallback shapes we attach them at the top level.
        `speed` is a factor (<1.0 = slower); `stability` is 0–1.
        """
        settings: dict[str, float] = {}
        if speed != 1.0:
            settings["speed"] = speed
        if stability is not None:
            settings["stability"] = stability
        if not settings:
            return
        target = (payload["generated_audio_inputs"]
                  if isinstance(payload.get("generated_audio_inputs"), dict)
                  else payload)
        target.update(settings)

    def submit_audio_generation(
        self, *, text: str, voice_id: str, model_id: str | None = None,
        speed: float = 1.0, stability: float | None = None,
        tts_model_id: str | None = None, language: str | None = None,
        workspace_id: str | None = None, tts_model_slug: str | None = None,
    ) -> tuple[str, str]:
        """POST a text_to_speech request, return (path, response_id).

        The canonical shape (captured from the live Hedra web-app request)
        is FLAT — speed/stability are only honoured in this form, and they
        require the TTS `model_id`:

            {"type": "text_to_speech", "voice_id": ..., "model_id": <tts>,
             "text": ..., "stability": 0.75, "speed": 0.9,
             "language": "Russian"}

        Hedra resolves `model_id` to a `model_slug` (e.g.
        "elevenlabs/elevenlabs-v3-331"). Pinned variants like `-331` may be
        entitled/priced differently and can fail with 402 even when the
        account has credits, so `tts_model_slug` lets us request the plain
        model ("elevenlabs/elevenlabs-v3") explicitly. When a slug is given
        it is tried FIRST, without model_id.

        We then fall back to the older nested/flat shapes.
        NB: `workspace_id` routes billing/credits to a specific Hedra
        workspace when the account uses more than one.
        """
        def _base() -> dict:
            payload = {
                "type": "text_to_speech",
                "voice_id": voice_id,
                "text": text,
            }
            if language:
                payload["language"] = language
            if speed != 1.0:
                payload["speed"] = speed
            if stability is not None:
                payload["stability"] = stability
            return payload

        attempts: list[tuple[str, dict]] = []

        # 1) Preferred: explicit model_slug (plain model, no pinned variant).
        if tts_model_slug:
            by_slug = _base()
            by_slug["model_slug"] = tts_model_slug
            attempts.append(("/generations", by_slug))

        # 2) Canonical web-app shape via model_id.
        canonical = _base()
        if tts_model_id:
            canonical["model_id"] = tts_model_id
        attempts.append(("/generations", canonical))

        for path, tpl in self._AUDIO_ATTEMPTS:
            payload = self._fill_template(
                tpl, text=text, voice_id=voice_id, model_id=model_id
            )
            if model_id is None and any(
                isinstance(v, str) and "{model_id}" in v for v in str(payload)
            ):
                continue
            self._inject_voice_settings(payload, speed, stability)
            attempts.append((path, payload))

        # Route every attempt to the funded workspace when provided.
        if workspace_id:
            for _path, _payload in attempts:
                _payload["workspace_id"] = workspace_id

        import json as _json
        # The slug attempt (when present) and the model_id attempt are both
        # "primary" — anything after them is a legacy-shape fallback.
        n_primary = 2 if tts_model_slug else 1
        last_err: HedraError | None = None
        for idx, (path, payload) in enumerate(attempts):
            is_canonical = idx < n_primary
            LOGGER.info("audio_attempt",
                        extra={"path": path, "is_canonical": is_canonical,
                               "variant": payload.get("model_slug")
                                          or payload.get("model_id") or "legacy",
                               "payload": _json.dumps(payload, ensure_ascii=False),
                               "speed": speed, "stability": stability,
                               "tts_model_id": tts_model_id, "language": language})
            try:
                resp = self._request("POST", path, json=payload)
            except HedraInsufficientBalance:
                # Out of credits. Walking the remaining payload variants can
                # only produce 422s that then mask the real cause in the
                # manifest, so surface the 402 as-is.
                LOGGER.error("audio_attempt_no_balance",
                             extra={"path": path, "attempt_index": idx})
                raise
            except HedraError as exc:
                level = LOGGER.warning if is_canonical else LOGGER.info
                level("audio_attempt_failed",
                      extra={"path": path, "is_canonical": is_canonical,
                             "err": str(exc)[:300]})
                last_err = exc
                continue
            data = resp.json() if resp.text else {}
            audio_id = (
                data.get("id")
                or data.get("audio_id")
                or data.get("asset_id")
                or data.get("generation_id")
            )
            if audio_id:
                if not is_canonical:
                    LOGGER.warning(
                        "audio_fallback_used",
                        extra={"path": path, "attempt_index": idx,
                               "payload": _json.dumps(payload, ensure_ascii=False),
                               "note": "canonical payload was rejected; voice/"
                                       "speed may differ from Hedra UI"})
                LOGGER.info("audio_submit_ok",
                            extra={"path": path, "is_canonical": is_canonical,
                                   "audio_id": audio_id,
                                   "response": _json.dumps(data, ensure_ascii=False)[:500]})
                return path, str(audio_id)
            last_err = HedraError(
                f"{path} accepted but returned no id: {data}"
            )
        raise HedraError(
            f"submit_audio_generation: no endpoint accepted the request. "
            f"Last error: {last_err}"
        )

    # ------------------------------------------------------------ generations
    def submit_generation(
        self,
        *,
        ai_model_id: str,
        avatar_asset_id: str,
        text: str,
        voice_id: str = "aisala",
        audio_id: str | None = None,
        resolution: str = "540p",
        aspect_ratio: str = "1:1",
        duration_seconds_max: int = 120,
        workspace_id: str | None = None,
    ) -> str:
        """POST /generations — submit a generation job, return generation_id.

        Hedra uses a Pydantic 2 discriminated union: `type=video` selects
        the VideoGenerationRequest variant. Errors come back tagged with
        the discriminator (`body.video.ai_model_id`), but the JSON itself
        must be FLAT — the `video` segment in the error path is the tag,
        not a nested object.
        """
        if not audio_id:
            raise HedraError(
                "submit_generation requires audio_id; Hedra rejected "
                "video_with_audio one-shot. Use submit_audio_generation first."
            )
        # Hedra requires text_prompt inside generated_video_inputs even
        # when audio_id is provided (used for lip-sync alignment).
        # NB: duration_ms is omitted on purpose — when audio_id is given,
        # Hedra MUST derive the duration from the audio asset. Passing
        # duration_ms forces the video to that exact length and stretches
        # audio with silence (~2 min videos for 30s narration).
        video_inputs: dict[str, Any] = {
            "text_prompt": text,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "audio_id": audio_id,
        }
        payload = {
            "type": "video",
            "ai_model_id": ai_model_id,
            "start_keyframe_id": avatar_asset_id,
            "audio_id": audio_id,
            "generated_video_inputs": video_inputs,
        }
        if workspace_id:
            payload["workspace_id"] = workspace_id
        LOGGER.info("submit_generation_payload",
                    extra={"payload": payload})
        resp = self._request("POST", "/generations", json=payload)
        data: dict[str, Any] = resp.json()
        gen_id = data.get("id") or data.get("generation_id")
        if not gen_id:
            raise HedraError(
                f"submit_generation: no generation id in response: {data}"
            )
        return str(gen_id)

    def get_generation_status(self, generation_id: str) -> dict[str, Any]:
        """GET /generations/{id}/status."""
        resp = self._request("GET", f"/generations/{generation_id}/status")
        return resp.json()

    def get_generation(self, generation_id: str) -> dict[str, Any]:
        """GET /generations/{id} — fallback for deployments without /status."""
        resp = self._request("GET", f"/generations/{generation_id}")
        return resp.json()

    # ----------------------------------------------------------------- download
    def download(self, url: str, dest: Path) -> None:
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with self.session.get(
            url, headers=self._headers(), timeout=self.timeout, stream=True
        ) as resp:
            if resp.status_code != 200:
                raise HedraError(
                    f"download {url} → {resp.status_code}: {resp.text[:200]}"
                )
            with dest.open("wb") as fh:
                for chunk in resp.iter_content(chunk_size=1024 * 256):
                    if chunk:
                        fh.write(chunk)
