"""Unit tests for HedraClient with mocked HTTP. Covers T-U-HC-1..5."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from l7.service.hedra_client import (
    HedraClient,
    HedraError,
    HedraInsufficientBalance,
)


def _make_session(responses):
    """responses: list of dicts {status, json}; returns a MagicMock session.

    When the scripted list is exhausted, returns 404 — keeps tests
    tolerant of the multi-endpoint discovery in list_voices().
    """
    session = MagicMock()
    iterator = iter(responses)

    def _request(method, url, **kwargs):
        try:
            item = next(iterator)
        except StopIteration:
            item = {"status": 404, "json": {"error": "exhausted"}}
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


# T-U-HC-3a — submit_generation requires audio_id (Hedra dropped
# video_with_audio in 2026; only video/image/text_to_speech are supported).
def test_submit_generation_requires_audio_id(hedra_env):
    session = _make_session([])
    client = HedraClient(session=session)
    with pytest.raises(HedraError) as exc:
        client.submit_generation(
            ai_model_id="model-abc-uuid",
            avatar_asset_id="asset_x",
            text="hello world",
            voice_id="voice-uuid",
        )
    assert "audio_id" in str(exc.value)


# T-U-HC-3b — with audio_id, video payload still carries text_prompt
# (Hedra uses it for lip-sync alignment with the pre-generated audio).
def test_submit_generation_payload_with_audio_id(hedra_env):
    session = _make_session([{"status": 200, "json": {"id": "gen_99"}}])
    client = HedraClient(session=session)
    gid = client.submit_generation(
        ai_model_id="model-abc-uuid",
        avatar_asset_id="asset_x",
        text="hello world",
        voice_id="voice-uuid",
        audio_id="audio-abc",
        resolution="540p",
        aspect_ratio="1:1",
    )
    assert gid == "gen_99"
    body = session.request.call_args.kwargs["json"]
    assert body["type"] == "video"
    assert body["audio_id"] == "audio-abc"
    inputs = body["generated_video_inputs"]
    assert inputs["audio_id"] == "audio-abc"
    assert inputs["text_prompt"] == "hello world"
    # voice_id is omitted in the video step — TTS already happened.
    assert "voice_id" not in inputs
    # duration_ms MUST NOT be sent — Hedra would force a 2-min video and
    # stretch the audio with silence. Length comes from the audio asset.
    assert "duration_ms" not in inputs


# T-U-HC-7 — audio generation uses type=text_to_speech and tries shapes
# until one succeeds.
def test_submit_audio_generation_fallback(hedra_env):
    session = _make_session([
        {"status": 422, "json": {"messages": ["wrong shape"]}},
        {"status": 200, "json": {"id": "audio_42"}},
    ])
    client = HedraClient(session=session)
    path, audio_id = client.submit_audio_generation(
        text="hello", voice_id="voice-uuid"
    )
    assert audio_id == "audio_42"
    assert "/generations" in path


# T-U-HC-6 — resolve_video_model_id picks the closest model by name.
def test_resolve_video_model_id_by_name(hedra_env):
    session = _make_session([
        {"status": 200, "json": [
            {"id": "uuid-old",  "name": "Character-1",       "type": "video"},
            {"id": "uuid-540",  "name": "Hedra Avatar 540p", "type": "video"},
            {"id": "uuid-720",  "name": "Hedra Avatar 720p", "type": "video"},
        ]},
    ])
    client = HedraClient(session=session)
    mid = client.resolve_video_model_id(name_hint="Hedra Avatar 540p")
    assert mid == "uuid-540"


def test_resolve_video_model_id_matches_avatar_keyword(hedra_env):
    """When the hint doesn't match, fall back to a model with 'avatar' in name."""
    session = _make_session([
        {"status": 200, "json": [
            {"id": "uuid-kling", "name": "Kling 1.6 T2V",       "type": "video"},
            {"id": "uuid-hedra", "name": "Hedra Avatar 1080p",  "type": "video"},
        ]},
    ])
    client = HedraClient(session=session)
    mid = client.resolve_video_model_id(name_hint="nonexistent")
    assert mid == "uuid-hedra"


def test_resolve_voice_id_by_name(hedra_env):
    session = _make_session([
        {"status": 200, "json": [
            {"id": "v-en-1", "name": "Adam",   "language": "en"},
            {"id": "v-ru-1", "name": "aisala", "language": "ru"},
            {"id": "v-ru-2", "name": "Nikita", "language": "ru"},
        ]},
    ])
    client = HedraClient(session=session)
    assert client.resolve_voice_id(name_hint="aisala") == "v-ru-1"


def test_resolve_voice_id_raises_when_unknown(hedra_env):
    session = _make_session([
        {"status": 200, "json": [
            {"id": "v-1", "name": "Adam"},
        ]},
    ])
    client = HedraClient(session=session)
    with pytest.raises(HedraError) as exc:
        client.resolve_voice_id(name_hint="nonexistent")
    assert "not found" in str(exc.value)


def test_resolve_video_model_id_raises_when_no_hedra_match(hedra_env):
    """Raise (not silently pick a Kling/Veo model) when no Hedra/avatar match."""
    session = _make_session([
        {"status": 200, "json": [
            {"id": "uuid-kling", "name": "Kling 1.6 T2V",  "type": "video"},
            {"id": "uuid-veo",   "name": "Veo 3 I2V",      "type": "video"},
        ]},
    ])
    client = HedraClient(session=session)
    with pytest.raises(HedraError) as exc:
        client.resolve_video_model_id(name_hint="nonexistent")
    assert "no Hedra avatar model" in str(exc.value)


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
def test_missing_api_key_fails_fast(monkeypatch, tmp_path):
    monkeypatch.delenv("HEDRA_API_KEY", raising=False)
    # Also hide any real ~/.hedra_key — otherwise this passes or fails
    # depending on whether the machine running the tests has a key on disk.
    monkeypatch.setattr(HedraClient, "_KEY_FILES", (str(tmp_path / "absent"),))
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


# A 402 means no credits; walking the remaining payload variants can only
# produce 422s that then mask the real cause. Fail fast on the 402 instead.
def test_insufficient_balance_stops_variant_walk(hedra_env):
    session = _make_session([
        {"status": 402, "json": {"error_code": "INSUFFICIENT_BALANCE",
                                 "credits_needed": 12, "credits_available": 5}},
        # Any further variant would 422 — must never be reached.
        {"status": 422, "json": {"messages": ["Field required"]}},
    ])
    client = HedraClient(session=session)
    with pytest.raises(HedraInsufficientBalance) as exc:
        client.submit_audio_generation(
            text="привет", voice_id="v1",
            tts_model_slug="elevenlabs/elevenlabs-v3",
            workspace_id="58237",
        )
    assert "INSUFFICIENT_BALANCE" in str(exc.value)
    # Exactly one POST: the walk stopped instead of burning the fallbacks.
    assert session.request.call_count == 1


def test_insufficient_balance_is_a_hedra_error(hedra_env):
    assert issubclass(HedraInsufficientBalance, HedraError)
