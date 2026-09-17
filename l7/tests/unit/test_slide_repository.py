"""Unit tests for SlideRepository. Covers T-U-SR-1..5."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from l7.service.slide_repository import (
    Slide,
    SlideRepository,
    SlidesSchemaError,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
REAL_SLIDES = REPO_ROOT / "l7/data/slides.json"
REAL_SCHEMA = REPO_ROOT / "l7/data/slides.schema.json"


# T-U-SR-1, T-U-SR-2 — all 50 slides have required fields and contiguous ids.
def test_real_slides_load_and_have_50_unique_contiguous_ids():
    repo = SlideRepository(REAL_SLIDES, REAL_SCHEMA)
    repo.load()
    slides = list(repo.iter_slides())
    assert len(slides) == 50
    ids = [s.id for s in slides]
    assert ids == list(range(1, 51))
    for s in slides:
        assert s.id and s.title and s.narration


# T-U-SR-3 — text_sha256 is deterministic.
def test_text_sha256_deterministic(tmp_lecture: Path):
    repo = SlideRepository(tmp_lecture / "data/slides.json")
    repo.load()
    slides = list(repo.iter_slides())
    again = list(SlideRepository(tmp_lecture / "data/slides.json").iter_slides() if True else [])
    again_repo = SlideRepository(tmp_lecture / "data/slides.json")
    again_repo.load()
    again = list(again_repo.iter_slides())
    for a, b in zip(slides, again):
        assert a.text_sha256 == b.text_sha256
        assert len(a.text_sha256) == 64


# T-U-SR-4 — missing narration ⇒ SlidesSchemaError.
def test_missing_narration_raises(tmp_lecture: Path):
    f = tmp_lecture / "data/slides.json"
    raw = json.loads(f.read_text(encoding="utf-8"))
    raw["slides"][1].pop("narration")
    f.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SlidesSchemaError) as exc:
        SlideRepository(f).load()
    assert "narration" in str(exc.value)


# T-U-SR-2 (variant) — duplicate ids rejected.
def test_duplicate_ids_rejected(tmp_lecture: Path):
    f = tmp_lecture / "data/slides.json"
    raw = json.loads(f.read_text(encoding="utf-8"))
    raw["slides"][1]["id"] = raw["slides"][0]["id"]
    f.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SlidesSchemaError):
        SlideRepository(f).load()


# T-U-SR-5 — schema validation matches loader behaviour.
def test_schema_validation_matches_loader(tmp_lecture: Path):
    # Drop a required field and verify both schema + loader raise.
    f = tmp_lecture / "data/slides.json"
    raw = json.loads(f.read_text(encoding="utf-8"))
    raw["slides"][0].pop("title")
    f.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(SlidesSchemaError):
        SlideRepository(f, REAL_SCHEMA).load()


# filename_pattern was a config key the pipeline silently ignored. Honouring it
# must not move a single existing file: every other dataset uses "{id}.mp4".
def test_filename_defaults_to_id(tmp_path: Path):
    s = Slide(id=7, title="T", narration="n")
    assert s.filename() == "7.mp4"
    assert s.filename("{id}.mp4") == "7.mp4"


def test_filename_uses_slug_when_pattern_asks(tmp_path: Path):
    s = Slide(id=1, title="AI-Enabled", narration="n", slug="01_level_ai_enabled")
    assert s.filename("{slug}.mp4") == "01_level_ai_enabled.mp4"
    # id stays available in the same pattern
    assert s.filename("{id}-{slug}.mp4") == "1-01_level_ai_enabled.mp4"


def test_slug_pattern_falls_back_to_id_when_dataset_has_no_slugs(tmp_path: Path):
    """A slug-less dataset under a {slug} pattern must still produce a name."""
    s = Slide(id=12, title="T", narration="n")
    assert s.filename("{slug}.mp4") == "12.mp4"


def test_slug_is_read_from_slides_json(tmp_path: Path):
    p = tmp_path / "slides.json"
    p.write_text(json.dumps({
        "lecture": {"id": "levels_en", "title": "T", "language": "en"},
        "slides": [
            {"id": 1, "slug": "01_a", "title": "A", "narration": "one"},
            {"id": 2, "title": "B", "narration": "two"},
        ],
    }, ensure_ascii=False), encoding="utf-8")
    slides = list(SlideRepository(p).iter_slides())
    assert slides[0].slug == "01_a"
    assert slides[1].slug == ""          # absent slug is empty, not None
    assert slides[0].filename("{slug}.mp4") == "01_a.mp4"
    assert slides[1].filename("{slug}.mp4") == "2.mp4"


def test_slug_does_not_affect_text_hash(tmp_path: Path):
    """Adding a slug must not invalidate idempotency for already-rendered text."""
    a = Slide(id=1, title="T", narration="same text")
    b = Slide(id=1, title="T", narration="same text", slug="01_x")
    assert a.text_sha256 == b.text_sha256
