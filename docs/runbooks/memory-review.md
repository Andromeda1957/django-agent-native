# Memory Review Runbook

Use when the user asks to review, audit, or improve the memory system.

## Goal

Make memory self-limiting. A review should identify objective failures, not
reopen the whole design every session.

## Fixed Review

1. Run `git status --short`.
2. Run `python3 tools/check_memory_system.py`.
3. Check only these rubric items:
   - Required memory/runbook files exist.
   - `AGENT_HANDOFF.md` contains current active state only.
   - Topic memory has `Current` sections separated from history.
   - Every topic memory file is routed from `PROJECT_MEMORY.md`.
   - `docs/plans/` contains only resumable deferred, blocked, or postponed work,
     not retired records that belong in `docs/site_history/`.
   - Every active plan is indexed in `docs/plans/README.md`.
   - Dated or volatile current facts have explicit verification anchors.
   - External service claims are scoped to what repo/server/public-site checks
     can actually verify.
   - Agent-facing instructions do not override the repo startup hierarchy.
   - Reported user failures are addressed at the smallest durable layer.
   - Structural recommendations are based on the whole relevant memory system,
     not a partial read or search-only scan.
4. If the automated check passes and no rubric item fails, say the memory system
   is healthy and do not propose structural revisions.
5. If a rubric item fails, propose or make only the smallest change that fixes
   that failure.

## Anti-Churn Rule

Do not propose structural memory revisions when checks pass. Do not re-propose
accepted tradeoffs from `docs/memory/workflow.md` as new issues unless fresh
evidence shows they are causing failures.

## Completion

For actual memory changes, follow `docs/runbooks/memory-maintenance.md`.
