"""Git add/commit/push with retry. Covers NR-F4-1..F4-3, NFR-F4-*."""

from __future__ import annotations

import logging
import subprocess
import time
from pathlib import Path

LOGGER = logging.getLogger("l7.git")

BACKOFFS = (2.0, 4.0, 8.0, 16.0)
MAX_BATCH_BYTES = 500 * 1024 * 1024  # 500 MB per NFR-F4-1


class GitError(RuntimeError):
    pass


class GitPublisher:
    def __init__(self, repo_root: Path, branch: str) -> None:
        self.repo_root = Path(repo_root)
        self.branch = branch

    def _run(self, *args: str) -> str:
        LOGGER.info("git", extra={"cmd": list(args)})
        try:
            out = subprocess.run(
                ("git", *args),
                cwd=self.repo_root,
                check=True,
                capture_output=True,
                text=True,
            )
            return out.stdout.strip()
        except subprocess.CalledProcessError as exc:
            raise GitError(
                f"git {' '.join(args)} → {exc.returncode}\n{exc.stderr}"
            ) from exc

    def _push_with_retry(self) -> None:
        last: BaseException | None = None
        for attempt, delay in enumerate((0.0, *BACKOFFS)):
            if delay:
                time.sleep(delay)
            try:
                self._run("push", "-u", "origin", self.branch)
                return
            except GitError as exc:
                LOGGER.warning(
                    "git_push_failed",
                    extra={"attempt": attempt, "delay": delay, "err": str(exc)},
                )
                last = exc
        raise GitError(f"git push retries exhausted: {last}")

    def publish(self, paths: list[Path], *, commit_message: str) -> None:
        total = sum(Path(p).stat().st_size for p in paths if Path(p).exists())
        if total > MAX_BATCH_BYTES:
            raise GitError(
                f"batch size {total} > 500MB limit (NFR-F4-1) — use Git LFS"
            )
        # Stage only the requested paths to keep blast radius small.
        rels = [str(Path(p).resolve().relative_to(self.repo_root.resolve())) for p in paths]
        self._run("add", "--", *rels)

        status = self._run("status", "--porcelain")
        if not status.strip():
            LOGGER.info("git_nothing_to_commit")
            return

        self._run("commit", "-m", commit_message)
        self._push_with_retry()
