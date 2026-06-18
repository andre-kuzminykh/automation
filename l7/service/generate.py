"""CLI orchestrator for video generation pipeline.

Covers F1, F2 end-to-end:
  generate.py  --lecture l7
              [--regenerate 1,7,12]
              [--from N --to M]
              [--limit N]
              [--dry-run]
              [--no-git]
              [--config l7/data/config.json]

Exit codes:
  0  — all OK
  1  — some slides failed
  2  — network/Hedra fatal
  3  — slides.json schema error
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Sequence

from .git_publisher import GitError, GitPublisher
from .hedra_client import HedraClient, HedraError
from .logging_setup import setup_logging
from .manifest_store import ManifestStore
from .slide_repository import SlideRepository, SlidesSchemaError

LOGGER = logging.getLogger("l7.generate")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="generate.py")
    p.add_argument("--lecture", default="l7", help="lecture id (used to find paths)")
    p.add_argument(
        "--config",
        type=Path,
        default=None,
        help="path to config.json; default l7/data/config.json",
    )
    p.add_argument(
        "--regenerate",
        type=str,
        default="",
        help="comma-separated slide ids to force re-generate",
    )
    p.add_argument("--from", dest="from_id", type=int, default=None)
    p.add_argument("--to", dest="to_id", type=int, default=None)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-git", action="store_true", help="skip git commit/push")
    p.add_argument(
        "--compress",
        action="store_true",
        default=True,
        help="ffmpeg re-encode each video before commit (libx264 crf 28). "
             "Hedra returns 50+ MB mp4s; default ON to fit GitHub limits.",
    )
    p.add_argument(
        "--no-compress",
        dest="compress",
        action="store_false",
        help="skip ffmpeg re-encoding (raw Hedra output)",
    )
    p.add_argument(
        "--speed", type=float, default=None,
        help="TTS speech speed sent to Hedra at generation time; "
             "0.75 = 25%% slower, 1.0 = unchanged (range ~0.7-1.2). "
             "Overrides config.hedra.speed.",
    )
    p.add_argument(
        "--stability", type=float, default=None,
        help="TTS voice stability 0-1 (higher = steadier/less expressive). "
             "Overrides config.hedra.stability.",
    )
    p.add_argument(
        "--poll-interval", type=float, default=5.0, help="seconds between polls"
    )
    p.add_argument(
        "--poll-timeout", type=float, default=600.0,
        help="seconds before giving up on one slide",
    )
    p.add_argument(
        "--max-consecutive-failures", type=int, default=3,
        help="abort the run after N consecutive submit failures",
    )
    p.add_argument(
        "--model-name",
        default="Hedra Avatar 540p",
        help="model name hint for resolve_video_model_id",
    )
    p.add_argument(
        "--ai-model-id",
        default=None,
        help="explicit Hedra ai_model_id; if set, skips /models lookup",
    )
    p.add_argument(
        "--list-models",
        action="store_true",
        help="print all Hedra models (id + name) and exit",
    )
    p.add_argument(
        "--list-voices",
        action="store_true",
        help="print all Hedra voices (id + name) and exit",
    )
    p.add_argument(
        "--voice-id",
        default=None,
        help="explicit Hedra voice_id UUID; if set, skips /voices lookup",
    )
    return p.parse_args(argv)


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(64 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _resolve_paths(lecture_root: Path, config: dict) -> dict[str, Path]:
    return {
        "slides": lecture_root / config["input"]["slides_file"],
        "schema": lecture_root / "data/slides.schema.json",
        "avatar": lecture_root / config["avatar_image"]["local_path"],
        "videos_dir": lecture_root / config["output"]["videos_dir"],
        "manifest": lecture_root / config["output"]["manifest_file"],
    }


def _load_config(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_id_set(raw: str) -> set[int]:
    if not raw:
        return set()
    return {int(x.strip()) for x in raw.split(",") if x.strip()}


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    log = setup_logging()

    repo_root = Path(__file__).resolve().parents[2]
    lecture_root = repo_root / args.lecture
    if not lecture_root.is_dir():
        log.error("lecture_dir_not_found", extra={"path": str(lecture_root)})
        return 3

    config_path = args.config or (lecture_root / "data/config.json")
    config = _load_config(config_path)
    paths = _resolve_paths(lecture_root, config)
    paths["videos_dir"].mkdir(parents=True, exist_ok=True)

    repo = SlideRepository(paths["slides"], paths["schema"])
    try:
        repo.load()
    except SlidesSchemaError as exc:
        log.error("slides_schema_error", extra={"err": str(exc)})
        return 3

    manifest = ManifestStore(paths["manifest"])
    manifest.load()
    manifest.set_top("lecture_id", repo.lecture.id)
    manifest.set_top("voice_id", config["hedra"]["voice_id"])

    regen = _parse_id_set(args.regenerate)
    from_id = args.from_id or 1
    to_id = args.to_id or len(repo)
    slides = [
        s for s in repo.iter_slides() if from_id <= s.id <= to_id
    ]
    if args.limit:
        slides = slides[: args.limit]

    if args.dry_run:
        log.info(
            "dry_run_plan",
            extra={
                "n_slides": len(slides),
                "regenerate": sorted(regen),
                "from": from_id,
                "to": to_id,
            },
        )
        return 0

    # --- Hedra setup ----------------------------------------------------------
    client = HedraClient()

    if args.list_models:
        try:
            models = client.list_models()
        except HedraError as exc:
            log.error("list_models_failed", extra={"err": str(exc)})
            return 2
        for m in models:
            mid = m.get("id") or m.get("ai_model_id") or "?"
            name = m.get("name") or "?"
            mtype = m.get("type") or m.get("model_type") or "?"
            print(f"{mid}\t{mtype:8s}\t{name}")
        print(f"\nTotal: {len(models)} models")
        return 0

    if args.list_voices:
        try:
            voices = client.list_voices()
        except HedraError as exc:
            log.error("list_voices_failed", extra={"err": str(exc)})
            return 2
        for v in voices:
            vid = v.get("id") or v.get("voice_id") or "?"
            name = v.get("name") or v.get("display_name") or "?"
            lang = v.get("language") or v.get("locale") or ""
            print(f"{vid}\t{lang:8s}\t{name}")
        print(f"\nTotal: {len(voices)} voices")
        return 0
    avatar_asset_id = manifest.data.get("avatar_asset_id")
    if not avatar_asset_id:
        if not paths["avatar"].exists():
            log.error("avatar_missing", extra={"path": str(paths["avatar"])})
            return 2
        try:
            avatar_asset_id = client.create_image_asset(name="lecture7-avatar")
            client.upload_asset_binary(avatar_asset_id, paths["avatar"])
        except HedraError as exc:
            log.error("avatar_upload_failed", extra={"err": str(exc)})
            return 2
        manifest.set_top("avatar_asset_id", avatar_asset_id)
        manifest.write_atomic()

    # Resolve the AI model ID once for the whole run.
    ai_model_id = args.ai_model_id or manifest.data.get("ai_model_id")
    if not ai_model_id:
        try:
            ai_model_id = client.resolve_video_model_id(name_hint=args.model_name)
        except HedraError as exc:
            log.error("model_resolution_failed", extra={"err": str(exc)})
            return 2
        manifest.set_top("ai_model_id", ai_model_id)
        manifest.write_atomic()
    log.info("ai_model_id_resolved", extra={"ai_model_id": ai_model_id})

    # Resolve the voice id (UUID). Hedra rejects display-name `voice_id`
    # values with "video generation without valid audio input".
    # Precedence: --voice-id > manifest cache > config.voice_id_known > /voices lookup.
    voice_id = (
        args.voice_id
        or manifest.data.get("voice_id_uuid")
        or config["hedra"].get("voice_id_known")
    )
    voice_hint = config["hedra"].get("voice_id", "aisala")
    if not voice_id:
        try:
            voice_id = client.resolve_voice_id(name_hint=voice_hint)
        except HedraError as exc:
            log.error("voice_resolution_failed", extra={"err": str(exc)})
            return 2
    manifest.set_top("voice_id_uuid", voice_id)
    manifest.set_top("voice_name", voice_hint)
    manifest.write_atomic()
    log.info("voice_id_resolved",
             extra={"voice_id": voice_id, "voice_name": voice_hint})

    # Voice tuning: CLI flag wins, else config.hedra, else default.
    tts_speed = (args.speed if args.speed is not None
                 else float(config["hedra"].get("speed", 1.0)))
    tts_stability = (args.stability if args.stability is not None
                     else config["hedra"].get("stability"))
    if tts_stability is not None:
        tts_stability = float(tts_stability)
    log.info("voice_tuning",
             extra={"speed": tts_speed, "stability": tts_stability})

    ok, skipped, failed = [], [], []
    consecutive_failures = 0

    for slide in slides:
        target_file = paths["videos_dir"] / f"{slide.id}.mp4"
        prev = manifest.get_slide(slide.id)

        # Idempotency check (NR-F1-9)
        if (
            slide.id not in regen
            and target_file.exists()
            and prev.get("text_sha256") == slide.text_sha256
            and prev.get("status") == "ok"
        ):
            log.info("slide_skip", extra={"slide": slide.id})
            skipped.append(slide.id)
            continue

        try:
            audio_id: str | None = None
            log.info("slide_audio_submit", extra={"slide": slide.id})
            audio_path, audio_gen_id = client.submit_audio_generation(
                text=slide.narration, voice_id=voice_id,
                model_id=ai_model_id, speed=tts_speed, stability=tts_stability,
            )
            # If the endpoint returned a generation_id (not yet ready),
            # poll for it. Asset ids from /audio are usable immediately.
            audio_id = audio_gen_id
            if "/generations" in audio_path:
                deadline = time.monotonic() + args.poll_timeout
                while time.monotonic() < deadline:
                    try:
                        st = client.get_generation_status(audio_gen_id)
                    except HedraError:
                        st = client.get_generation(audio_gen_id)
                    status = (st.get("status") or "").lower()
                    if status in {"complete", "completed", "succeeded", "ok"}:
                        audio_id = (
                            st.get("asset_id")
                            or st.get("audio_id")
                            or st.get("output_id")
                            or audio_gen_id
                        )
                        break
                    if status in {"failed", "error"}:
                        raise HedraError(
                            f"audio generation failed: {st.get('error')}"
                        )
                    time.sleep(args.poll_interval)
            log.info("slide_audio_ok",
                     extra={"slide": slide.id, "audio_id": audio_id})

            log.info("slide_submit", extra={"slide": slide.id})
            generation_id = client.submit_generation(
                ai_model_id=ai_model_id,
                avatar_asset_id=avatar_asset_id,
                text=slide.narration,
                voice_id=voice_id,
                audio_id=audio_id,
                resolution=config["hedra"]["resolution"],
                aspect_ratio=config["hedra"]["aspect_ratio"],
            )
        except HedraError as exc:
            log.error("slide_submit_failed", extra={"slide": slide.id, "err": str(exc)})
            manifest.merge_slide_result(
                slide.id, status="failed", error=str(exc),
                text_sha256=slide.text_sha256,
            )
            manifest.write_atomic()
            failed.append(slide.id)
            consecutive_failures += 1
            if consecutive_failures >= args.max_consecutive_failures:
                log.error(
                    "abort_consecutive_failures",
                    extra={"count": consecutive_failures,
                           "threshold": args.max_consecutive_failures},
                )
                print(
                    f"ABORT: {consecutive_failures} consecutive submit failures "
                    f"(structural error?). Stopping run."
                )
                break
            continue

        manifest.merge_slide_result(
            slide.id,
            status="submitted",
            hedra_generation_id=generation_id,
            text_sha256=slide.text_sha256,
        )
        manifest.write_atomic()

        # Poll (NR-F1-3, UC-F1-1-4)
        deadline = time.monotonic() + args.poll_timeout
        result: dict | None = None
        while time.monotonic() < deadline:
            try:
                result = client.get_generation_status(generation_id)
            except HedraError:
                # try the alternative GET shape
                try:
                    result = client.get_generation(generation_id)
                except HedraError as exc:
                    log.warning(
                        "poll_transient_error",
                        extra={"slide": slide.id, "err": str(exc)},
                    )
                    time.sleep(args.poll_interval)
                    continue
            status = (result.get("status") or "").lower()
            if status in {"complete", "completed", "succeeded", "ok"}:
                break
            if status in {"failed", "error"}:
                break
            time.sleep(args.poll_interval)

        if not result or (result.get("status") or "").lower() not in {
            "complete", "completed", "succeeded", "ok",
        }:
            err = (result or {}).get("error", "timeout")
            log.error(
                "slide_failed",
                extra={"slide": slide.id, "status": (result or {}).get("status"), "err": err},
            )
            manifest.merge_slide_result(
                slide.id, status="failed", error=str(err),
                hedra_generation_id=generation_id,
                text_sha256=slide.text_sha256,
            )
            manifest.write_atomic()
            failed.append(slide.id)
            continue

        video_url = (
            result.get("video_url")
            or result.get("url")
            or (result.get("output") or {}).get("video_url")
        )
        if not video_url:
            log.error("no_video_url", extra={"slide": slide.id, "result": result})
            manifest.merge_slide_result(
                slide.id, status="failed",
                error="no video_url in response",
                hedra_generation_id=generation_id,
                text_sha256=slide.text_sha256,
            )
            manifest.write_atomic()
            failed.append(slide.id)
            continue

        try:
            client.download(video_url, target_file)
        except HedraError as exc:
            log.error("download_failed", extra={"slide": slide.id, "err": str(exc)})
            manifest.merge_slide_result(
                slide.id, status="failed", error=f"download: {exc}",
                hedra_generation_id=generation_id,
                text_sha256=slide.text_sha256,
            )
            manifest.write_atomic()
            failed.append(slide.id)
            continue

        size = target_file.stat().st_size
        sha = _file_sha256(target_file)
        manifest.merge_slide_result(
            slide.id,
            status="ok",
            hedra_generation_id=generation_id,
            text_sha256=slide.text_sha256,
            file_sha256=sha,
            duration_sec=None,  # could be measured with ffprobe; out of MVP
        )
        manifest.write_atomic()
        log.info(
            "slide_ok",
            extra={"slide": slide.id, "size": size, "sha256": sha[:8]},
        )
        ok.append(slide.id)
        consecutive_failures = 0

    # --- Summary (NR-F1-8) ----------------------------------------------------
    summary = (
        f"OK: {len(ok)} / SKIPPED: {len(skipped)} / FAILED: {len(failed)}"
    )
    print(summary)
    if failed:
        print(f"FAILED ids: {sorted(failed)}")

    # --- Compress videos (NFR-F4-1: keep batch ≤ 500 MB) ---------------------
    if args.compress and ok:
        for sid in sorted(ok):
            src = paths["videos_dir"] / f"{sid}.mp4"
            if not src.exists():
                continue
            size_before = src.stat().st_size
            if size_before < 5 * 1024 * 1024:  # < 5 MB — no need
                continue
            tmp = src.with_suffix(".compressed.mp4")
            log.info("compress_start",
                     extra={"slide": sid, "size_before": size_before})
            import subprocess
            try:
                subprocess.run(
                    ["ffmpeg", "-y", "-i", str(src),
                     "-vcodec", "libx264", "-crf", "28", "-preset", "fast",
                     "-acodec", "aac", "-b:a", "96k", "-movflags", "+faststart",
                     str(tmp)],
                    check=True, capture_output=True,
                )
            except (subprocess.CalledProcessError, FileNotFoundError) as exc:
                log.warning("compress_skipped",
                            extra={"slide": sid, "err": str(exc)[:200]})
                tmp.unlink(missing_ok=True)
                continue
            size_after = tmp.stat().st_size
            tmp.replace(src)
            log.info("compress_ok",
                     extra={"slide": sid, "size_before": size_before,
                            "size_after": size_after,
                            "ratio": round(size_after / max(size_before, 1), 3)})

    # --- Git publish (F4) -----------------------------------------------------
    if not args.no_git and ok:
        publisher = GitPublisher(repo_root, config["git"]["branch"])
        paths_to_commit = [paths["videos_dir"] / f"{i}.mp4" for i in sorted(ok)]
        paths_to_commit.append(paths["manifest"])
        try:
            publisher.publish(
                paths_to_commit,
                commit_message=(
                    "feat(l7): add hedra-generated videos for lecture 7 "
                    f"({len(ok)} slides)"
                ),
            )
        except GitError as exc:
            log.error("git_publish_failed", extra={"err": str(exc)})
            return 1

    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
