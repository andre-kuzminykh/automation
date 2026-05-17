"""Unit tests for ManifestStore. Covers T-U-MS-1..4."""

from __future__ import annotations

import json
from pathlib import Path

from l7.service.manifest_store import ManifestStore


# T-U-MS-1 — write_atomic uses tmp+rename.
def test_write_atomic_writes_target(tmp_path: Path):
    target = tmp_path / "manifest.json"
    store = ManifestStore(target)
    store.load()
    store.merge_slide_result(1, status="ok", text_sha256="abc")
    store.write_atomic()
    assert target.exists()
    data = json.loads(target.read_text(encoding="utf-8"))
    assert data["slides"]["1"]["status"] == "ok"
    # tmp file shouldn't linger after successful write
    assert not target.with_suffix(".json.tmp").exists()


# T-U-MS-2 — if a previous run left a half-written file, store rotates it to .broken.json.
def test_corrupt_manifest_rotated(tmp_path: Path):
    target = tmp_path / "manifest.json"
    target.write_text("{not valid json", encoding="utf-8")
    store = ManifestStore(target)
    store.load()
    # rotated to .broken.json
    rotated = target.with_suffix(".broken.json")
    assert rotated.exists()
    assert store.data == {"slides": {}}


# T-U-MS-3 — output is UTF-8 without BOM, 2-space indent, sorted keys.
def test_write_format(tmp_path: Path):
    target = tmp_path / "manifest.json"
    store = ManifestStore(target)
    store.load()
    store.merge_slide_result(2, status="ok", text_sha256="zzz")
    store.merge_slide_result(1, status="ok", text_sha256="aaa")
    store.write_atomic()
    raw = target.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf"), "must not contain BOM"
    text = raw.decode("utf-8")
    assert '  "slides"' in text  # 2-space indent
    # sorted keys: "slides" before any later key alphabetically
    lines = text.splitlines()
    slide_indices = [i for i, ln in enumerate(lines) if '"1"' in ln or '"2"' in ln]
    assert slide_indices[0] < slide_indices[1]  # "1" appears before "2"


# T-U-MS-4 — merging a new slide doesn't drop the existing ones.
def test_merge_preserves_neighbours(tmp_path: Path):
    target = tmp_path / "manifest.json"
    store = ManifestStore(target)
    store.load()
    store.merge_slide_result(1, status="ok", text_sha256="x1")
    store.write_atomic()
    store2 = ManifestStore(target)
    store2.load()
    store2.merge_slide_result(2, status="ok", text_sha256="x2")
    store2.write_atomic()
    final = json.loads(target.read_text(encoding="utf-8"))
    assert final["slides"]["1"]["status"] == "ok"
    assert final["slides"]["2"]["status"] == "ok"
