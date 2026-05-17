"""Shared pytest fixtures for l7 tests."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture
def tmp_lecture(tmp_path: Path) -> Path:
    """A temporary lecture directory with minimal slides.json."""
    (tmp_path / "data").mkdir()
    (tmp_path / "videos").mkdir()
    slides = {
        "lecture": {"id": "l7", "title": "Test", "language": "ru"},
        "slides": [
            {"id": 1, "title": "T1", "narration": "narration one"},
            {"id": 2, "title": "T2", "narration": "narration two"},
            {"id": 3, "title": "T3", "narration": "narration three"},
        ],
    }
    (tmp_path / "data/slides.json").write_text(
        json.dumps(slides, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return tmp_path


@pytest.fixture
def hedra_env(monkeypatch):
    monkeypatch.setenv("HEDRA_API_KEY", "sk_hedra_TEST_KEY_xxxxxxxx")
