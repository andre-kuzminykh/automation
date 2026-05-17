"""Unit tests for HedraClient with mocked HTTP. Covers T-U-HC-1..5."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from l7.service.hedra_client import HedraClient, HedraError


def _make_session(responses):
    """responses: list of dicts {status, json}; returns a MagicMock session."""
    session = MagicMock()
    iterator = iter(responses)

    def _request(method, url, **kwargs):
        item = next(iterator)
        resp = MagicMock()
        resp.status_code = item["status"]
        resp.json.return_value = item.get("json", {})
        resp.text = json.dumps(item.get("json", {}))
        return resp

    session.request.side_effect = _request
    return session


# T-U-HC-1 — create_image_asset POSTs to /assets and returns id.
def test_create_image_asset(hedra_env):
    session = _make_session([{"status": 200, "json": {"id": "asset_123"}}])
    client = HedraClient(session=session)
    asset_id = client.create_image_asset("test-name")
    assert asset_id == "asset_123"
    call = session.request.call_args
    assert call[0][0] == "POST"
    assert call[0][1].endswith("/assets")
    assert call.kwargs["json"]["type"] == "image"
    assert call.kwargs["headers"]["X-API-KEY"].startswith("sk_hedra_")


# T-U-HC-2 — upload_asset_binary uses multipart POST to /assets/{id}/upload.
def test_upload_asset_binary(hedra_env, tmp_path: Path):
    img = tmp_path / "x.jpg"
    img.write_bytes(b"\xff\xd8\xff\xe0fakejpeg")
    session = _make_session([{"status": 200, "json": {}}])
    client = HedraClient(session=session)
    client.upload_asset_binary("asset_x", img)
    call = session.request.call_args
    assert call[0][0] == "POST"
    assert "/assets/asset_x/upload" in call[0][1]
    assert "files" in call.kwargs


# T-U-HC-3 — submit_generation passes model, voice, resolution, aspect_ratio.
def test_submit_generation_payload(hedra_env):
    session = _make_session([{"status": 200, "json": {"id": "gen_77"}}])
    client = HedraClient(session=session)
    gid = client.submit_generation(
        avatar_asset_id="asset_x",
        text="hello world",
        voice_id="aisala",
        model_name="Hedra Avatar 540p",
        resolution="540p",
        aspect_ratio="1:1",
    )
    assert gid == "gen_77"
    body = session.request.call_args.kwargs["json"]
    assert body["ai_model_name"] == "Hedra Avatar 540p"
    assert body["start_keyframe_id"] == "asset_x"
    inputs = body["generated_video_inputs"]
    assert inputs["text_prompt"] == "hello world"
    assert inputs["voice_id"] == "aisala"
    assert inputs["resolution"] == "540p"
    assert inputs["aspect_ratio"] == "1:1"


# T-U-HC-4 — get_generation_status returns parsed JSON.
def test_get_generation_status(hedra_env):
    session = _make_session([
        {"status": 200, "json": {"status": "in_progress"}},
        {"status": 200, "json": {"status": "complete", "video_url": "https://x/y.mp4"}},
    ])
    client = HedraClient(session=session)
    assert client.get_generation_status("gen_1")["status"] == "in_progress"
    assert client.get_generation_status("gen_1")["status"] == "complete"


# T-U-HC-5 — missing API key fails fast; key never appears in error text.
def test_missing_api_key_fails_fast(monkeypatch):
    monkeypatch.delenv("HEDRA_API_KEY", raising=False)
    with pytest.raises(HedraError) as exc:
        HedraClient()
    assert "HEDRA_API_KEY" in str(exc.value)


# Negative — error response surfaces a HedraError with status and snippet.
def test_error_response_raises(hedra_env):
    session = _make_session([
        {"status": 400, "json": {"error": "bad"}},
    ])
    client = HedraClient(session=session)
    with pytest.raises(HedraError) as exc:
        client.create_image_asset("x")
    assert "400" in str(exc.value)
