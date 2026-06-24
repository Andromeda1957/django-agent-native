---
name: long-running-project-memory
description: >-
  Design, audit, or repair this project's repo-backed memory system for
  long-lived agent continuity. Use when the user asks about agent instructions,
  runbooks, handoffs, topic memory, changelogs, multi-agent continuity, stale
  facts, or memory-system enforcement.
---

# Long-running project memory

Use this skill to keep the memory system durable, small, and usable by every
agent that touches the repo. The goal is repo-backed continuity, not hidden model
memory or chat-only notes.

## Core model

Keep six layers separate:

1. Agent contract: small, stable behavior rules.
2. Runbooks: repeatable task workflows and completion checklists.
3. Active handoff: current state only, short-lived and replaceable.
4. Topic memory: current durable facts by domain.
5. Plans: deferred or multi-phase implementation plans.
6. History: append-only changelog and archived/deprecated notes.

No single file should carry all six layers.

## Source hierarchy

- `AGENTS.md` for the canonical agent contract.
- `CLAUDE.md` as an exact byte-for-byte mirror of `AGENTS.md` (regenerate with
  `python3 tools/sync_agents.py`).
- `GEMINI.md` as a separate read-only overlay (not a mirror).
- `docs/runbooks/` for required workflows.
- `AGENT_HANDOFF.md` for current active state only.
- `PROJECT_MEMORY.md` as the memory router and topic index.
- `docs/memory/` for current durable facts.
- `docs/plans/` for deferred implementation plans.
- `docs/site_history/` for archived context and retired plans.
- Code, config, and command output for implementation truth.
- `CHANGELOG.md` for completed history only.

Fresh command output beats stored memory for live facts. Current sections beat
deprecated or historical sections. External notes and agent memories are leads,
not authority.

## Workflow

1. Follow the startup contract in `AGENTS.md`.
2. Read `PROJECT_MEMORY.md` only as an index, then read the relevant topic memory
   and runbook files.
3. For memory reviews, use `docs/runbooks/memory-review.md`; if the automated
   check and fixed rubric pass, report the system healthy instead of proposing
   speculative redesigns.
4. For actual memory changes, use `docs/runbooks/memory-maintenance.md` and
   `docs/runbooks/docs-change.md`.
5. Before edits or long-running work, apply `docs/runbooks/task-memory-triage.md`
   and create tracking memory only when the triage warrants it.
6. Identify whether the change belongs to behavior, workflow, active state,
   durable fact, or history before editing.
7. Edit the smallest appropriate repo-backed file.
8. Preserve useful old context as historical context instead of deleting it.
9. Verify with `git diff --check` and `python3 tools/check_memory_system.py`.
10. Record completed maintenance in `CHANGELOG.md` and commit locally.

## Placement rules

- Put behavior and source-of-truth rules in `AGENTS.md`, then regenerate
  `CLAUDE.md` with `tools/sync_agents.py`.
- Put reusable task steps in `docs/runbooks/*.md`.
- Put active resumable state only in `AGENT_HANDOFF.md`.
- Put durable current facts, setup, decisions, and gotchas in
  `docs/memory/<topic>.md`.
- Put deferred implementation plans in `docs/plans/*.md`.
- Put completed work in `CHANGELOG.md`.
- Put archived context and retired plans in `docs/site_history/*.md`.
- Do not put completed history in `AGENT_HANDOFF.md`.
- Do not leave retired plans in `docs/plans/`.
- Do not expand `AGENTS.md`/`CLAUDE.md` for ordinary topic-memory changes.
