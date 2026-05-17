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
        avatar_asset_id: str,
        text: str,
        voice_id: str = "aisala",
        model_name: str = "Hedra Avatar 540p",
        resolution: str = "540p",
        aspect_ratio: str = "1:1",
        duration_seconds_max: int = 120,
    ) -> str:
        """POST /generations — submit a generation job, return generation_id.

        The body shape follows Hedra's current public web-app API. If the
        provider tightens the spec, only this method needs to change.
        """
        payload = {
            "type": "video",
            "ai_model_name": model_name,
            "start_keyframe_id": avatar_asset_id,
            "generated_video_inputs": {
                "text_prompt": text,
                "voice_id": voice_id,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
                "duration_ms": duration_seconds_max * 1000,
            },
        }
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
