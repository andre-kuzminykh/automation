"""Git add/commit/push with retry. Covers NR-F4-1..F4-3, NFR-F4-*."""

from __future__ import annotations

import logging
import os
import subprocess
import time
from pathlib import Path

LOGGER = logging.getLogger("l7.git")

BACKOFFS = (2.0, 4.0, 8.0, 16.0)
MAX_BATCH_BYTES = 500 * 1024 * 1024  # 500 MB per NFR-F4-1


class GitError(RuntimeError):
    pass


_AUTH_MARKERS = (
    "authentication failed",
    "invalid username or token",
    "password authentication is not supported",
    "could not read username",
    "could not read password",
    "permission denied (publickey)",
    "fatal: could not read",
)


def _is_auth_failure(err: "GitError") -> bool:
    msg = str(err).lower()
    return any(m in msg for m in _AUTH_MARKERS)


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
                # Make sure git won't sit on a credentials prompt forever.
                env={**os.environ,
                     "GIT_TERMINAL_PROMPT": "0",
                     "GIT_ASKPASS": "/bin/true"},
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
                if _is_auth_failure(exc):
                    raise GitError(
                        "git push: authentication failed — no retry.\n"
                        "Fix with one of:\n"
                        "  • PAT in URL:  git remote set-url origin "
                        "https://<USER>:<PAT>@github.com/<owner>/<repo>.git\n"
                        "  • SSH:         git remote set-url origin "
                        "git@github.com:<owner>/<repo>.git  (with SSH key on VM)\n"
                        f"Original error:\n{exc}"
                    ) from exc
                LOGGER.warning(
                    "git_push_failed",
                    extra={"attempt": attempt, "delay": delay, "err": str(exc)},
                )
                last = exc
        raise GitError(f"git push retries exhausted: {last}")

    def _ensure_identity(self) -> None:
        """Set a placeholder git identity if none is configured.

        Without this, `git commit` fails on a fresh VM with
        "Author identity unknown". User can override post-hoc.
        """
        try:
            self._run("config", "user.email")
            self._run("config", "user.name")
            return
        except GitError:
            pass
        import getpass, socket
        email = f"{getpass.getuser()}@{socket.gethostname()}"
        name = getpass.getuser()
        LOGGER.warning(
            "git_identity_autoconfig",
            extra={"email": email, "name": name,
                   "note": "override with: git config --global user.email/name"},
        )
        self._run("config", "user.email", email)
        self._run("config", "user.name", name)

    def publish(self, paths: list[Path], *, commit_message: str) -> None:
        total = sum(Path(p).stat().st_size for p in paths if Path(p).exists())
        if total > MAX_BATCH_BYTES:
            raise GitError(
                f"batch size {total} > 500MB limit (NFR-F4-1) — use Git LFS"
            )
        self._ensure_identity()
        # Stage only the requested paths to keep blast radius small.
        rels = [str(Path(p).resolve().relative_to(self.repo_root.resolve())) for p in paths]
        self._run("add", "--", *rels)

        status = self._run("status", "--porcelain")
        if not status.strip():
            LOGGER.info("git_nothing_to_commit")
            return

        self._run("commit", "-m", commit_message)
        self._push_with_retry()
