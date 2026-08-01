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


# T-U-MS-5 — concurrent generators each hold a snapshot from load(); writing
# must replay only own changes onto the current file, never dump the snapshot.
def test_concurrent_stores_do_not_lose_entries(tmp_path: Path):
    target = tmp_path / "manifest.json"

    # Both load the same (empty) state up front, as parallel workers do.
    a, b = ManifestStore(target), ManifestStore(target)
    a.load()
    b.load()

    a.merge_slide_result(1, status="ok", text_sha256="x1")
    a.write_atomic()

    # b's snapshot predates slide 1 — its write must not erase it.
    b.merge_slide_result(2, status="ok", text_sha256="x2")
    b.write_atomic()

    final = json.loads(target.read_text(encoding="utf-8"))
    assert set(final["slides"]) == {"1", "2"}
    assert final["slides"]["1"]["text_sha256"] == "x1"
    assert final["slides"]["2"]["text_sha256"] == "x2"


# T-U-MS-6 — same for top-level keys written by a stale snapshot.
def test_concurrent_top_level_keys_survive(tmp_path: Path):
    target = tmp_path / "manifest.json"
    a, b = ManifestStore(target), ManifestStore(target)
    a.load()
    b.load()

    a.set_top("avatar_asset_id", "avatar-1")
    a.write_atomic()

    b.set_top("voice_id_uuid", "voice-1")
    b.write_atomic()

    final = json.loads(target.read_text(encoding="utf-8"))
    assert final["avatar_asset_id"] == "avatar-1"
    assert final["voice_id_uuid"] == "voice-1"


# T-U-MS-7 — real parallel processes hammering one manifest lose nothing.
def test_multiprocess_writes_lose_nothing(tmp_path: Path):
    import multiprocessing as mp

    target = tmp_path / "manifest.json"

    def worker(slide_id: int) -> None:
        store = ManifestStore(target)
        store.load()
        store.merge_slide_result(slide_id, status="ok", text_sha256=f"h{slide_id}")
        store.write_atomic()

    ctx = mp.get_context("fork")
    procs = [ctx.Process(target=worker, args=(i,)) for i in range(1, 13)]
    for p in procs:
        p.start()
    for p in procs:
        p.join(30)

    final = json.loads(target.read_text(encoding="utf-8"))
    assert set(final["slides"]) == {str(i) for i in range(1, 13)}
