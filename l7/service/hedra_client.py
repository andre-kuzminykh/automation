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
        self.api_key = api_key or os.environ.get("HEDRA_API_KEY")
        if not self.api_key:
            raise HedraError(
                "HEDRA_API_KEY is required (env var) — refusing to start"
            )
        self.session = session or requests.Session()

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
            raise HedraError(
                f"{method} {path} → {resp.status_code}: {body}"
            )
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

    # ------------------------------------------------------------ generations
    def submit_generation(
        self,
        *,
        ai_model_id: str,
        avatar_asset_id: str,
        text: str,
        voice_id: str = "aisala",
        resolution: str = "540p",
        aspect_ratio: str = "1:1",
        duration_seconds_max: int = 120,
    ) -> str:
        """POST /generations — submit a generation job, return generation_id.

        Hedra uses a Pydantic 2 discriminated union: `type=video` selects
        the VideoGenerationRequest variant. Errors come back tagged with
        the discriminator (`body.video.ai_model_id`), but the JSON itself
        must be FLAT — the `video` segment in the error path is the tag,
        not a nested object.
        """
        payload = {
            "type": "video",
            "ai_model_id": ai_model_id,
            "start_keyframe_id": avatar_asset_id,
            "generated_video_inputs": {
                "text_prompt": text,
                "voice_id": voice_id,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "duration_ms": duration_seconds_max * 1000,
            },
        }
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
