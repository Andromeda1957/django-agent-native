"""Regenerate agent-entrypoint mirrors from the canonical contract.

`AGENTS.md` is the single source of truth for the agent operating contract.
Some agents look for a differently named file, so this script copies `AGENTS.md`
verbatim to those mirrors. Run it after editing `AGENTS.md`:

    python3 tools/sync_agents.py            # regenerate mirrors
    python3 tools/sync_agents.py --check    # verify mirrors are current (CI)

GEMINI.md is intentionally NOT a mirror — it is a narrower read-only overlay
with its own content — so it is not managed here.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CANONICAL = "AGENTS.md"
MIRRORS = ["CLAUDE.md"]


def main() -> int:
    check = "--check" in sys.argv[1:]
    source = (ROOT / CANONICAL).read_text(encoding="utf-8")

    drift = []
    for mirror in MIRRORS:
        path = ROOT / mirror
        current = path.read_text(encoding="utf-8") if path.exists() else None
        if current == source:
            continue
        if check:
            drift.append(mirror)
        else:
            path.write_text(source, encoding="utf-8")
            print(f"synced {mirror} <- {CANONICAL}")

    if check and drift:
        joined = ", ".join(drift)
        print(f"agent mirrors are stale: {joined}. Run: python3 tools/sync_agents.py")
        return 1

    if not check and not drift:
        print("mirrors up to date")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
