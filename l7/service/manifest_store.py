"""Atomic manifest read/write. Covers NR-F2-4, NR-F2-5, NFR-F2-2, NFR-F1-6."""

from __future__ import annotations

import fcntl
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


class ManifestStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._data: dict[str, Any] = {}
        # Keys this process has touched since load(). Parallel generators each
        # hold a snapshot taken at startup; on write we must replay only our own
        # changes onto the current file, never dump the whole stale snapshot.
        self._dirty_slides: set[str] = set()
        self._dirty_top: set[str] = set()

    def load(self) -> dict[str, Any]:
        if self.path.exists():
            try:
                self._data = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                # Corrupted file — start fresh but keep the broken one for diagnostics.
                self.path.rename(self.path.with_suffix(".broken.json"))
                self._data = {}
        else:
            self._data = {}
        self._data.setdefault("slides", {})
        return self._data

    @property
    def data(self) -> dict[str, Any]:
        return self._data

    @contextmanager
    def _locked(self) -> Iterator[None]:
        """Cross-process exclusive lock, so read-modify-write can't interleave."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        lock_path = self.path.with_suffix(self.path.suffix + ".lock")
        with open(lock_path, "w", encoding="utf-8") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)

    def _on_disk(self) -> dict[str, Any]:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {"slides": {}}
        if not isinstance(data, dict):
            return {"slides": {}}
        data.setdefault("slides", {})
        return data

    def write_atomic(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._locked():
            # Merge onto the *current* file, not our startup snapshot: with N
            # generators running in parallel, dumping the snapshot would drop
            # every slide the other N-1 processes wrote since we loaded.
            merged = self._on_disk()
            for key in self._dirty_top:
                merged[key] = self._data.get(key)
            slides = merged.setdefault("slides", {})
            for sid in self._dirty_slides:
                slides[sid] = self._data["slides"][sid]

            # Unique tmp name per process: parallel generators must not share one
            # manifest.json.tmp (concurrent os.replace would FileNotFoundError).
            tmp = self.path.with_suffix(self.path.suffix + f".tmp.{os.getpid()}")
            payload = json.dumps(
                merged, ensure_ascii=False, indent=2, sort_keys=True
            )
            tmp.write_text(payload, encoding="utf-8")
            os.replace(tmp, self.path)

        # Keep the in-memory view consistent with what we just persisted.
        self._data = merged

    def merge_slide_result(
        self,
        slide_id: int,
        *,
        status: str,
        hedra_generation_id: str | None = None,
        text_sha256: str | None = None,
        file_sha256: str | None = None,
        duration_sec: float | None = None,
        error: str | None = None,
    ) -> None:
        slides = self._data.setdefault("slides", {})
        prev = slides.get(str(slide_id), {})
        prev.update(
            {
                "status": status,
                "hedra_generation_id": hedra_generation_id
                if hedra_generation_id is not None
                else prev.get("hedra_generation_id"),
                "text_sha256": text_sha256
                if text_sha256 is not None
                else prev.get("text_sha256"),
                "file_sha256": file_sha256
                if file_sha256 is not None
                else prev.get("file_sha256"),
                "duration_sec": duration_sec
                if duration_sec is not None
                else prev.get("duration_sec"),
                "error": error,
                "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
        )
        slides[str(slide_id)] = prev
        self._dirty_slides.add(str(slide_id))

    def get_slide(self, slide_id: int) -> dict[str, Any]:
        return self._data.get("slides", {}).get(str(slide_id), {})

    def set_top(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._dirty_top.add(key)
