"""Reads & validates slides.json. Covers NR-F2-1..F2-3, NFR-F2-1."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


class SlidesSchemaError(ValueError):
    """Raised when slides.json fails validation."""


@dataclass(frozen=True)
class Slide:
    id: int
    title: str
    narration: str

    @property
    def text_sha256(self) -> str:
        return hashlib.sha256(self.narration.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Lecture:
    id: str
    title: str
    language: str
    subtitle: str = ""
    course: str = ""


class SlideRepository:
    def __init__(self, slides_path: Path, schema_path: Path | None = None) -> None:
        self.slides_path = Path(slides_path)
        self.schema_path = Path(schema_path) if schema_path else None
        self._raw: dict | None = None
        self._lecture: Lecture | None = None
        self._slides: list[Slide] | None = None

    def load(self) -> None:
        try:
            self._raw = json.loads(self.slides_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SlidesSchemaError(f"slides.json not valid JSON: {exc}") from exc

        if self.schema_path and self.schema_path.exists():
            self._validate_schema()

        self._validate_content()

    def _validate_schema(self) -> None:
        try:
            import jsonschema
        except ImportError:
            return
        schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
        try:
            jsonschema.validate(instance=self._raw, schema=schema)
        except jsonschema.ValidationError as exc:
            raise SlidesSchemaError(
                f"slides.json schema validation failed: {exc.message}"
            ) from exc

    def _validate_content(self) -> None:
        raw = self._raw or {}
        lecture_raw = raw.get("lecture") or {}
        slides_raw = raw.get("slides") or []

        if not isinstance(slides_raw, list) or not slides_raw:
            raise SlidesSchemaError("slides.json: 'slides' must be a non-empty array")

        seen_ids: set[int] = set()
        slides: list[Slide] = []
        for idx, item in enumerate(slides_raw):
            if not isinstance(item, dict):
                raise SlidesSchemaError(f"slide #{idx}: must be an object")
            for field in ("id", "title", "narration"):
                if field not in item or not item[field]:
                    raise SlidesSchemaError(
                        f"slide #{idx}: missing/empty required field '{field}'"
                    )
            sid = int(item["id"])
            if sid in seen_ids:
                raise SlidesSchemaError(f"duplicate slide id={sid}")
            seen_ids.add(sid)
            slides.append(
                Slide(
                    id=sid,
                    title=str(item["title"]),
                    narration=str(item["narration"]),
                )
            )

        slides.sort(key=lambda s: s.id)
        expected = list(range(1, len(slides) + 1))
        actual = [s.id for s in slides]
        if actual != expected:
            raise SlidesSchemaError(
                f"slide ids must be contiguous 1..N; got {actual}"
            )

        self._slides = slides
        self._lecture = Lecture(
            id=str(lecture_raw.get("id", "")),
            title=str(lecture_raw.get("title", "")),
            language=str(lecture_raw.get("language", "ru")),
            subtitle=str(lecture_raw.get("subtitle", "")),
            course=str(lecture_raw.get("course", "")),
        )

    @property
    def lecture(self) -> Lecture:
        if self._lecture is None:
            self.load()
        assert self._lecture is not None
        return self._lecture

    def iter_slides(self) -> Iterator[Slide]:
        if self._slides is None:
            self.load()
        assert self._slides is not None
        return iter(self._slides)

    def __len__(self) -> int:
        if self._slides is None:
            self.load()
        return len(self._slides or [])
