# Workflow & Memory System

How agents work in this repo and how the memory system stays healthy.

## Current Setup

- The agent operating contract is `AGENTS.md` (canonical), mirrored byte-for-byte
  to `CLAUDE.md` by `tools/sync_agents.py`. `GEMINI.md` is a separate read-only
  overlay.
- Required workflows live in `docs/runbooks/`. Active state lives in
  `AGENT_HANDOFF.md`. Durable facts live in `docs/memory/` topic files.
- Deferred or multi-phase work is planned in `docs/plans/`.
- History lives in `CHANGELOG.md`; archived/retired context lives in
  `docs/site_history/`. Neither overrides current state.
- `tools/check_memory_system.py` enforces the shape of all of the above and runs
  in pre-commit and CI.

## Current Rules

- Keep `AGENT_HANDOFF.md` to current active state only (max 120 lines).
- Every `docs/memory/*.md` file uses the standard section shape: Current Setup,
  Current Rules, Runbooks, Lookup Anchors, Deprecated / Historical.
- After editing `AGENTS.md`, run `python3 tools/sync_agents.py` and
  `python3 tools/check_memory_system.py`.
- Record completed work in `CHANGELOG.md`; record durable facts in topic memory;
  do not duplicate history into the handoff.

## Runbooks

- Memory maintenance: `docs/runbooks/memory-maintenance.md`.
- Memory review: `docs/runbooks/memory-review.md`.
- Documentation/repo-maintenance changes: `docs/runbooks/docs-change.md`.
- Security gate for runtime work: `docs/runbooks/security-implementation.md`.

## Lookup Anchors

- Contract: `AGENTS.md`. Router: `PROJECT_MEMORY.md`.
- Enforcement: `tools/check_memory_system.py`, `.claude/hooks/floor_gate.py`.
- Plans layer: `docs/plans/`. Archive layer: `docs/site_history/`.

## Accepted Baseline / Known Tradeoffs

- This is a personal-to-small-team scale starter, not enterprise SOC tooling.
- The `floor_gate.py` completion gate is Claude-only by design; other agents
  rely on the contract plus CI.
- Memory shape is enforced mechanically; content quality is the author's job.

## Deprecated / Historical

- None yet. Record superseded workflow facts here with the date they changed.
