#!/usr/bin/env python3
"""Claude-only completion-floor Stop gate.

WHAT
    Runs when Claude Code tries to END a turn (the `Stop` event). If this turn
    produced real repo work, it refuses to let the turn finish until the
    AGENTS.md completion floor is met:
        1. all changes are committed  (clean working tree),
        2. committed work from this session is pushed to the upstream branch,
        3. CHANGELOG.md was updated for work committed this session,
        4. `tools/check_memory_system.py` passes.

WHY
    Adherence to the completion contract is unreliable across turns. This moves
    the guarantee out of model behavior and into a deterministic gate. It checks
    for the PRESENCE of good closeout -- it deliberately does NOT block actions,
    because action-denial guards rot into stale traps. Check #4 is single-sourced
    to the project's own checker, not re-encoded here.

SCOPE / SAFETY
    Registered only in `.claude/settings.json`, so it affects Claude Code
    sessions only (other agents never read it). It is read-only: it inspects git
    state and runs a read-only checker. The only thing it writes is the
    per-session baseline ref under `.git/` (which git never reports in status).

    It does NOT enforce deploy -- a deploy cannot be checked from here without
    becoming the kind of fragile guard this gate exists to avoid, so deploy stays
    the runbook's responsibility. It does enforce pushing so GitHub CI sees the
    work.

IF THIS GATE IS EVER WRONG / IN THE WAY
    - One-shot bypass:  set env  SKIP_FLOOR_GATE=1
    - Remove it:        delete the "Stop" block in .claude/settings.json and
                        delete this file.
    Do not let it become a stale guard: if these checks stop matching the
    completion contract, fix or delete it.

USAGE
    SessionStart:  python3 .claude/hooks/floor_gate.py record   # baseline HEAD
    Stop:          python3 .claude/hooks/floor_gate.py          # the gate
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

SKIP_ENV = "SKIP_FLOOR_GATE"
REF_NAME = "agent_floor_session_ref"


def project_dir() -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=project_dir(),
        capture_output=True,
        text=True,
    )


def ref_path() -> str | None:
    result = git("rev-parse", "--git-dir")
    if result.returncode != 0:
        return None
    git_dir = result.stdout.strip()
    if not os.path.isabs(git_dir):
        git_dir = os.path.join(project_dir(), git_dir)
    return os.path.join(git_dir, REF_NAME)


def record_baseline() -> int:
    """SessionStart: remember HEAD so Stop can tell what this session changed."""
    head = git("rev-parse", "HEAD")
    path = ref_path()
    if head.returncode == 0 and path:
        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(head.stdout.strip() + "\n")
        except OSError:
            pass
    return 0


def read_baseline() -> str | None:
    path = ref_path()
    if not path or not os.path.exists(path):
        return None
    try:
        sha = open(path, encoding="utf-8").read().strip()
    except OSError:
        return None
    if not sha or git("cat-file", "-e", f"{sha}^{{commit}}").returncode != 0:
        return None
    return sha


def block(reason: str) -> None:
    # Exit code 2 tells Claude Code to refuse the stop and feed stderr back.
    sys.stderr.write(reason)
    sys.exit(2)


def upstream_ahead_count() -> tuple[str | None, int | None]:
    upstream = git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}")
    if upstream.returncode != 0:
        return None, None

    upstream_name = upstream.stdout.strip()
    counts = git("rev-list", "--left-right", "--count", f"{upstream_name}...HEAD")
    if counts.returncode != 0:
        return upstream_name, None

    parts = counts.stdout.split()
    if len(parts) != 2:
        return upstream_name, None

    try:
        ahead = int(parts[1])
    except ValueError:
        return upstream_name, None
    return upstream_name, ahead


def main() -> int:
    # Consume the Stop-event JSON on stdin; tolerate empty / non-JSON input.
    raw = "" if sys.stdin.isatty() else sys.stdin.read()
    try:
        json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        pass

    if os.environ.get(SKIP_ENV, "").strip().lower() in {"1", "true", "yes"}:
        sys.stderr.write(f"[floor-gate] bypassed via {SKIP_ENV}.\n")
        return 0

    porcelain = git("status", "--porcelain")
    dirty = porcelain.returncode == 0 and porcelain.stdout.strip() != ""

    head = git("rev-parse", "HEAD")
    head_sha = head.stdout.strip() if head.returncode == 0 else None
    baseline = read_baseline()

    committed_files: list[str] = []
    if baseline and head_sha and baseline != head_sha:
        diff = git("diff", "--name-only", f"{baseline}..{head_sha}")
        if diff.returncode == 0:
            committed_files = [line for line in diff.stdout.splitlines() if line.strip()]

    if not (dirty or committed_files):
        # No work to close out this turn (e.g. a pure-conversation turn).
        return 0

    # 1. Everything committed?
    if dirty:
        block(
            "[floor-gate] Completion floor not met: the working tree has "
            "uncommitted changes.\n\n"
            f"{porcelain.stdout.rstrip()}\n\n"
            "Per the AGENTS.md completion contract, commit completed repo work "
            "locally (updating CHANGELOG.md and AGENT_HANDOFF.md as the relevant "
            "runbook requires) before ending the turn.\n"
            f"Intentional exception? Set {SKIP_ENV}=1.\n"
        )

    # 2. Work pushed so GitHub CI/CD can see it?
    if committed_files:
        upstream_name, ahead = upstream_ahead_count()
        if upstream_name is None:
            block(
                "[floor-gate] Completion floor not met: work was committed this "
                "session, but the current branch has no configured upstream.\n\n"
                "Push the branch to your GitHub remote and set upstream "
                "(e.g. `git push -u origin HEAD`) before ending the turn so "
                "GitHub CI can run.\n"
                f"Intentional exception? Set {SKIP_ENV}=1.\n"
            )
        if ahead is None or ahead > 0:
            upstream_display = upstream_name or "upstream"
            ahead_display = "unknown" if ahead is None else str(ahead)
            block(
                "[floor-gate] Completion floor not met: committed work from this "
                "session is not pushed to GitHub.\n\n"
                f"Upstream: {upstream_display}\n"
                f"Commits ahead: {ahead_display}\n\n"
                "Push the completed commit(s) to your GitHub remote and wait for "
                "CI when the runbook requires it before ending the turn.\n"
                f"Intentional exception? Set {SKIP_ENV}=1.\n"
            )

    # 3. Work recorded in CHANGELOG.md? (only when the session diff is known)
    if committed_files and "CHANGELOG.md" not in committed_files:
        non_changelog = [name for name in committed_files if name != "CHANGELOG.md"]
        if non_changelog:
            joined = "\n  ".join(committed_files)
            block(
                "[floor-gate] Completion floor not met: work was committed this "
                "session but CHANGELOG.md was not updated.\n\n"
                f"Committed this session:\n  {joined}\n\n"
                "Per the completion contract, record completed work in "
                "CHANGELOG.md.\n"
                f"Intentional exception? Set {SKIP_ENV}=1.\n"
            )

    # 4. Memory-system shape valid? (single-sourced to the project's checker)
    checker = os.path.join(project_dir(), "tools", "check_memory_system.py")
    if os.path.exists(checker):
        result = subprocess.run(
            [sys.executable, checker],
            cwd=project_dir(),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            detail = (result.stdout + result.stderr).strip()
            block(
                "[floor-gate] Completion floor not met: "
                "tools/check_memory_system.py failed.\n\n"
                f"{detail}\n\n"
                "Fix the memory-system shape before finishing.\n"
                f"Intentional exception? Set {SKIP_ENV}=1.\n"
            )

    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    sys.exit(record_baseline() if mode == "record" else main())
