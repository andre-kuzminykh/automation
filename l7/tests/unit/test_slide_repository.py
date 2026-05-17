"""Unit tests for SlideRepository. Covers T-U-SR-1..5."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from l7.service.slide_repository import SlideRepository, SlidesSchemaError

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
