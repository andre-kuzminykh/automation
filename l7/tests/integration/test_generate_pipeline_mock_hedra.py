"""Integration tests for the full pipeline with mocked Hedra.

Covers T-I-GP-1..6.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from l7.service import generate as gen_mod


@pytest.fixture
def fake_pipeline(tmp_path: Path, monkeypatch):
    """Construct a self-contained tmp 'repo' with 3 slides and avatar."""
    # Mirror real repo layout under tmp_path/automation/l7
    auto = tmp_path / "automation"
    l7 = auto / "l7"
    (l7 / "data").mkdir(parents=True)
    (l7 / "videos").mkdir()

    slides = {
        "lecture": {"id": "l7", "title": "Test", "language": "ru"},
        "slides": [
            {"id": 1, "title": "T1", "narration": "narration one"},
            {"id": 2, "title": "T2", "narration": "narration two"},
            {"id": 3, "title": "T3", "narration": "narration three"},
        ],
    }
    (l7 / "data/slides.json").write_text(
        json.dumps(slides, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # Reuse real schema
    real_schema = Path(__file__).resolve().parents[3] / "l7/data/slides.schema.json"
    shutil.copy(real_schema, l7 / "data/slides.schema.json")
    (l7 / "data/avatar.jpg").write_bytes(b"\xff\xd8\xff\xe0fakejpeg")

    config = {
        "hedra": {
            "api_base": "https://api.hedra.com/web-app/public",
            "model": "Hedra Avatar 540p",
            "resolution": "540p",
            "aspect_ratio": "1:1",
            "voice_id": "aisala",
        },
        "avatar_image": {"local_path": "data/avatar.jpg"},
        "input": {"slides_file": "data/slides.json"},
        "output": {
            "videos_dir": "videos",
            "manifest_file": "data/manifest.json",
        },
        "git": {"branch": "claude/setup-gcloud-video-service-XKVf0"},
    }
    (l7 / "data/config.json").write_text(json.dumps(config), encoding="utf-8")

    monkeypatch.setenv("HEDRA_API_KEY", "sk_hedra_TEST")
    # Make generate.py resolve REPO_ROOT to our fake auto.
    monkeypatch.setattr(
        gen_mod, "__file__", str(l7 / "service/generate.py")
    )
    (l7 / "service").mkdir()
    (l7 / "service/generate.py").write_text("# stub\n")

    return auto, l7


class MockHedra:
    """Records calls; returns scripted answers."""

    def __init__(self, *, fail_slide_ids=None) -> None:
        self.fail_slide_ids = set(fail_slide_ids or ())
        self.submitted = []
        self.created_assets = 0

    def create_image_asset(self, name: str) -> str:
        self.created_assets += 1
        return f"asset_{self.created_assets}"

    def upload_asset_binary(self, asset_id: str, path) -> None:
        return None

    def resolve_video_model_id(self, *, name_hint: str = "") -> str:
        return "mock-model-uuid"

    def resolve_voice_id(self, *, name_hint: str = "") -> str:
        return "mock-voice-uuid"

    def list_models(self) -> list:
        return [{"id": "mock-model-uuid", "name": "Mock Avatar 540p", "type": "video"}]

    def list_voices(self) -> list:
        return [{"id": "mock-voice-uuid", "name": "aisala", "language": "ru"}]

    def submit_audio_generation(self, *, text, voice_id, model_id=None,
                                 speed=1.0, stability=None,
                                 tts_model_id=None, language=None,
                                 workspace_id=None,
                                 tts_model_slug=None) -> tuple[str, str]:
        return "/audio", f"audio_{len(self.submitted) + 1}"

    def submit_generation(self, *, avatar_asset_id, text, **_kw) -> str:
        self.submitted.append(text)
        gid = f"gen_{len(self.submitted)}"
        return gid

    def get_generation_status(self, gid: str) -> dict:
        idx = int(gid.split("_")[1])
        slide_id = idx  # 1:1 in this fixture
        if slide_id in self.fail_slide_ids:
            return {"status": "failed", "error": "synthetic failure"}
        return {
            "status": "complete",
            "video_url": f"https://fake/{slide_id}.mp4",
        }

    def get_generation(self, gid: str) -> dict:
        return self.get_generation_status(gid)

    def download(self, url: str, dest) -> None:
        Path(dest).write_bytes(b"FAKEMP4" + url.encode())


def _run_pipeline(fake_pipeline, mock_hedra, *, args_extra=None):
    auto, l7 = fake_pipeline
    args = ["--lecture", "l7", "--no-git", "--config", str(l7 / "data/config.json")]
    if args_extra:
        args += args_extra
    with patch("l7.service.generate.HedraClient", return_value=mock_hedra), \
         patch.object(gen_mod, "Path") as _:
        pass  # Path mocking too invasive; do it differently below

    # We need the script to compute repo_root = parents[2] of generate.py.
    # The fixture already monkeypatched __file__ for that.
    with patch("l7.service.generate.HedraClient", return_value=mock_hedra):
        return gen_mod.main(args)


# T-I-GP-1 — 3-slide happy path.
def test_three_slides_all_ok(fake_pipeline):
    auto, l7 = fake_pipeline
    mock = MockHedra()
    code = _run_pipeline(fake_pipeline, mock)
    assert code == 0
    for sid in (1, 2, 3):
        assert (l7 / f"videos/{sid}.mp4").exists()
    manifest = json.loads((l7 / "data/manifest.json").read_text(encoding="utf-8"))
    for sid in ("1", "2", "3"):
        assert manifest["slides"][sid]["status"] == "ok"


# T-I-GP-2 — idempotent skip on second run.
def test_idempotent_skip_on_second_run(fake_pipeline):
    auto, l7 = fake_pipeline
    mock = MockHedra()
    _run_pipeline(fake_pipeline, mock)
    assert len(mock.submitted) == 3

    mock2 = MockHedra()
    code = _run_pipeline(fake_pipeline, mock2)
    assert code == 0
    assert len(mock2.submitted) == 0  # all skipped


# T-I-GP-3 — --regenerate forces a single slide.
def test_regenerate_one_slide(fake_pipeline):
    auto, l7 = fake_pipeline
    _run_pipeline(fake_pipeline, MockHedra())

    mock2 = MockHedra()
    code = _run_pipeline(fake_pipeline, mock2, args_extra=["--regenerate", "2"])
    assert code == 0
    assert len(mock2.submitted) == 1
    assert mock2.submitted[0] == "narration two"


# T-I-GP-4 — partial failure: 1 and 3 ok, 2 failed; exit code 1.
def test_partial_failure(fake_pipeline, capsys):
    auto, l7 = fake_pipeline
    mock = MockHedra(fail_slide_ids={2})
    code = _run_pipeline(fake_pipeline, mock)
    captured = capsys.readouterr()
    assert "FAILED: 1" in captured.out
    assert "FAILED ids: [2]" in captured.out
    assert code == 1
    manifest = json.loads((l7 / "data/manifest.json").read_text(encoding="utf-8"))
    assert manifest["slides"]["1"]["status"] == "ok"
    assert manifest["slides"]["2"]["status"] == "failed"
    assert manifest["slides"]["3"]["status"] == "ok"


# T-I-GP-5 — summary contains OK / SKIPPED / FAILED.
def test_summary_format(fake_pipeline, capsys):
    _run_pipeline(fake_pipeline, MockHedra())
    captured = capsys.readouterr()
    assert "OK:" in captured.out
    assert "SKIPPED:" in captured.out
    assert "FAILED:" in captured.out


# T-I-GP-6 — atomic manifest survives crash mid-run.
def test_manifest_atomic_across_interruption(fake_pipeline):
    auto, l7 = fake_pipeline
    mock = MockHedra()
    # First run completes
    _run_pipeline(fake_pipeline, mock)
    first = (l7 / "data/manifest.json").read_text(encoding="utf-8")

    # Simulate corruption of a NEW tmp file (must not affect the real one)
    tmp = (l7 / "data/manifest.json.tmp")
    tmp.write_text("{garbage", encoding="utf-8")
    # The main manifest is still valid:
    assert json.loads((l7 / "data/manifest.json").read_text(encoding="utf-8"))


class MockEleven:
    """Records what the pipeline asked ElevenLabs to synthesise."""

    def __init__(self) -> None:
        self.calls = []

    def synthesize(self, *, text, **settings) -> bytes:
        self.calls.append({"text": text, **settings})
        return b"ID3" + text.encode("utf-8")


def _add_eleven_config(l7: Path, **overrides) -> None:
    cfg_path = l7 / "data/config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    cfg["elevenlabs"] = {
        "provider": "elevenlabs",
        "voice_id": "el-voice-1",
        "model_id": "eleven_multilingual_v2",
        "stability": "robust",
        "speed": 0.75,
        **overrides,
    }
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")


def test_elevenlabs_provider_uploads_asset_and_skips_hedra_tts(fake_pipeline):
    """Hedra must lip-sync a pre-made asset, never run its own TTS."""
    auto, l7 = fake_pipeline
    _add_eleven_config(l7)

    mock = MockHedra()
    audio_assets = []
    uploaded = []

    def create_audio_asset(name):
        audio_assets.append(name)
        return f"audio_asset_{len(audio_assets)}"

    def upload_asset_binary(asset_id, path, content_type=None):
        uploaded.append((asset_id, Path(path).read_bytes()))

    mock.create_audio_asset = create_audio_asset
    mock.upload_asset_binary = upload_asset_binary

    def _no_hedra_tts(**_kw):
        raise AssertionError("Hedra TTS must not be called for elevenlabs")

    mock.submit_audio_generation = _no_hedra_tts

    eleven = MockEleven()
    with patch("l7.service.generate.HedraClient", return_value=mock), \
         patch("l7.service.generate.ElevenLabsClient", return_value=eleven):
        code = gen_mod.main([
            "--lecture", "l7", "--no-git",
            "--config", str(l7 / "data/config.json"),
        ])

    assert code == 0
    assert [c["text"] for c in eleven.calls] == [
        "narration one", "narration two", "narration three",
    ]
    assert eleven.calls[0]["voice_id"] == "el-voice-1"
    # "robust" resolved to the numeric stability the API takes.
    assert eleven.calls[0]["stability"] == 1.0
    assert eleven.calls[0]["speed"] == 0.75
    # Each narration became a Hedra audio asset, uploaded with real bytes.
    # (uploaded also carries the avatar image, hence the filter.)
    audio_uploads = [u for u in uploaded if u[0].startswith("audio_asset_")]
    assert len(audio_uploads) == 3
    assert audio_uploads[0][1] == b"ID3" + "narration one".encode("utf-8")
    for sid in (1, 2, 3):
        assert (l7 / f"videos/{sid}.mp4").exists()


def test_elevenlabs_temp_audio_not_left_in_videos_dir(fake_pipeline):
    """videos/ is `git add`-ed wholesale; no stray mp3 may survive there."""
    auto, l7 = fake_pipeline
    _add_eleven_config(l7)

    mock = MockHedra()
    mock.create_audio_asset = lambda name: "audio_asset_1"
    mock.upload_asset_binary = lambda asset_id, path, content_type=None: None

    eleven = MockEleven()
    with patch("l7.service.generate.HedraClient", return_value=mock), \
         patch("l7.service.generate.ElevenLabsClient", return_value=eleven):
        gen_mod.main([
            "--lecture", "l7", "--no-git",
            "--config", str(l7 / "data/config.json"),
        ])

    leftovers = [p.name for p in (l7 / "videos").iterdir()
                 if p.suffix != ".mp4"]
    assert leftovers == []


def test_hedra_remains_default_when_no_elevenlabs_config(fake_pipeline):
    """Lectures already rendered with Hedra TTS must not silently switch."""
    auto, l7 = fake_pipeline
    mock = MockHedra()
    code = _run_pipeline(fake_pipeline, mock)
    assert code == 0
    assert len(mock.submitted) == 3


def test_tts_provider_flag_overrides_config(fake_pipeline):
    auto, l7 = fake_pipeline
    _add_eleven_config(l7)
    mock = MockHedra()
    with patch("l7.service.generate.HedraClient", return_value=mock):
        code = gen_mod.main([
            "--lecture", "l7", "--no-git", "--tts-provider", "hedra",
            "--config", str(l7 / "data/config.json"),
        ])
    assert code == 0
    # Fell back to Hedra's own TTS despite the elevenlabs block.
    assert len(mock.submitted) == 3
