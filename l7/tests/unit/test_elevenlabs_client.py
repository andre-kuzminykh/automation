"""Unit tests for ElevenLabsClient with mocked HTTP."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from l7.service.elevenlabs_client import (
    ElevenLabsClient,
    ElevenLabsError,
    resolve_stability,
)


@pytest.fixture
def el_env(monkeypatch, tmp_path):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk_test_aaaaaaaaaaaaaaaaaaaa")
    monkeypatch.setattr(ElevenLabsClient, "_KEY_FILES", (str(tmp_path / "absent"),))


def _make_session(responses):
    session = MagicMock()
    iterator = iter(responses)

    def _request(method, url, **kwargs):
        try:
            item = next(iterator)
        except StopIteration:
            item = {"status": 404, "text": "exhausted", "content": b""}
        resp = MagicMock()
        resp.status_code = item["status"]
        resp.content = item.get("content", b"")
        resp.text = item.get("text", "")
        resp.json.return_value = item.get("json", {})
        return resp

    session.request.side_effect = _request
    return session


def test_synthesize_returns_audio_bytes(el_env):
    session = _make_session([{"status": 200, "content": b"ID3fake-mp3-bytes"}])
    client = ElevenLabsClient(session=session)
    audio = client.synthesize(text="привет", voice_id="v1", speed=0.75)
    assert audio == b"ID3fake-mp3-bytes"

    method, url = session.request.call_args[0]
    assert method == "POST"
    assert url.endswith("/text-to-speech/v1")
    kwargs = session.request.call_args.kwargs
    assert kwargs["headers"]["xi-api-key"] == "sk_test_aaaaaaaaaaaaaaaaaaaa"
    assert kwargs["params"]["output_format"] == "mp3_44100_128"
    assert kwargs["json"]["text"] == "привет"
    assert kwargs["json"]["voice_settings"]["speed"] == 0.75


def test_empty_body_is_an_error(el_env):
    session = _make_session([{"status": 200, "content": b""}])
    client = ElevenLabsClient(session=session)
    with pytest.raises(ElevenLabsError) as exc:
        client.synthesize(text="x", voice_id="v1")
    assert "empty body" in str(exc.value)


# eleven_v3 rejects `speed`. Losing the narration over one unsupported knob
# would be worse than losing the knob — drop it, keep the audio, say so.
def test_rejected_setting_is_dropped_and_retried(el_env, caplog):
    session = _make_session([
        {"status": 422, "text": '{"detail":"speed is not supported for this model"}'},
        {"status": 200, "content": b"audio!"},
    ])
    client = ElevenLabsClient(session=session)
    with caplog.at_level("WARNING", logger="l7.elevenlabs"):
        audio = client.synthesize(
            text="x", voice_id="v1", model_id="eleven_v3",
            speed=0.75, stability=1.0,
        )
    assert audio == b"audio!"
    assert session.request.call_count == 2

    first = session.request.call_args_list[0].kwargs["json"]["voice_settings"]
    second = session.request.call_args_list[1].kwargs["json"]["voice_settings"]
    assert "speed" in first
    assert "speed" not in second
    # stability was not the offender, so it must survive.
    assert second["stability"] == 1.0

    dropped = next(r for r in caplog.records if r.msg == "tts_settings_dropped")
    assert dropped.dropped == ["speed"]


def test_unrelated_error_is_not_retried(el_env):
    session = _make_session([
        {"status": 401, "text": '{"detail":"invalid api key"}'},
        {"status": 200, "content": b"never reached"},
    ])
    client = ElevenLabsClient(session=session)
    with pytest.raises(ElevenLabsError) as exc:
        client.synthesize(text="x", voice_id="v1", speed=0.75)
    assert "401" in str(exc.value)
    assert session.request.call_count == 1


def test_422_naming_no_known_setting_raises(el_env):
    """A 422 that isn't about a voice_settings field must not loop forever."""
    session = _make_session([
        {"status": 422, "text": '{"detail":"text too long"}'},
    ])
    client = ElevenLabsClient(session=session)
    with pytest.raises(ElevenLabsError) as exc:
        client.synthesize(text="x", voice_id="v1", speed=0.75)
    assert "text too long" in str(exc.value)
    assert session.request.call_count == 1


def test_missing_key_fails_fast(monkeypatch, tmp_path):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.setattr(ElevenLabsClient, "_KEY_FILES", (str(tmp_path / "absent"),))
    with pytest.raises(ElevenLabsError) as exc:
        ElevenLabsClient()
    assert "ELEVENLABS_API_KEY" in str(exc.value)


def test_key_conflict_is_logged(monkeypatch, tmp_path, caplog):
    key_file = tmp_path / "el_key"
    key_file.write_text("sk_FILEKEY_bbbbbbbbbbbbbbbbbbbb", encoding="utf-8")
    monkeypatch.setattr(ElevenLabsClient, "_KEY_FILES", (str(key_file),))
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk_ENVKEY_aaaaaaaaaaaaaaaaaaaa")
    with caplog.at_level("INFO", logger="l7.elevenlabs"):
        client = ElevenLabsClient()
    assert client.api_key.startswith("sk_ENVKEY")
    assert "api_key_conflict" in [r.msg for r in caplog.records]
    blob = "".join(str(r.__dict__) for r in caplog.records)
    assert "sk_ENVKEY_aaaaaaaaaaaaaaaaaaaa" not in blob
    assert "sk_FILEKEY_bbbbbbbbbbbbbbbbbbbb" not in blob


@pytest.mark.parametrize("value,expected", [
    ("robust", 1.0), ("Robust", 1.0), ("natural", 0.5), ("creative", 0.0),
    (0.42, 0.42), ("0.3", None), (None, None),
])
def test_resolve_stability(value, expected):
    if value == "0.3":
        with pytest.raises(ElevenLabsError):
            resolve_stability(value)
        return
    assert resolve_stability(value) == expected


def test_list_voices(el_env):
    session = _make_session([
        {"status": 200, "json": {"voices": [{"voice_id": "v1", "name": "Andre"}]}},
    ])
    client = ElevenLabsClient(session=session)
    voices = client.list_voices()
    assert voices == [{"voice_id": "v1", "name": "Andre"}]
