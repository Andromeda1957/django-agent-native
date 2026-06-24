# Memory Maintenance Runbook

Use only when the user asks to update memory/docs, when the active task is memory
maintenance, or when stale memory would cause imminent risky action.

## Principles

- Keep `AGENTS.md` small and stable.
- Keep `AGENT_HANDOFF.md` current-state-only.
- Put current durable facts in `docs/memory/<topic>.md`.
- Put required workflow steps in `docs/runbooks/<workflow>.md`.
- Put history in `CHANGELOG.md`, `docs/site_history/`, or small
  `Deprecated / Historical` sections.
- Preserve old context instead of deleting it when it may be useful later.

## Steps

1. Identify whether the change is behavior, workflow, current fact, active state,
   or history.
2. Use `docs/runbooks/task-memory-triage.md` before editing if the maintenance
   task creates or changes a multi-phase plan, recurring workflow, or active
   handoff state.
3. Edit the smallest appropriate file.
4. Do not update agent entrypoints for ordinary topic-memory changes.
5. If you edit `AGENTS.md`, run `python3 tools/sync_agents.py` to regenerate the
   `CLAUDE.md` mirror.
6. Before committing, audit every `AGENT_HANDOFF.md` bullet. Each bullet must
   answer at least one of:
   - What is actively in progress?
   - What exact next action should resume?
   - What blocker needs owner or external input?
   - What immediate "do not do this now" fact prevents waste or risk?
   - What dirty worktree caveat would affect the next agent?
7. Move any handoff bullet that mainly summarizes completed work into
   `CHANGELOG.md`, `docs/memory/<topic>.md`, or `docs/site_history/` before
   closeout.
8. Make sure every `docs/memory/*.md` file is routed from `PROJECT_MEMORY.md` and
   every active `docs/plans/*.md` file is indexed in `docs/plans/README.md`.
9. Mark volatile current facts with `Last verified YYYY-MM-DD` and a recheck
   command or lookup anchor. Do not leave bare `as of YYYY-MM-DD` claims in
   `Current Setup`.
10. Scope external-service claims. For services outside repo/server/public-site
    verification, either verify them directly or label them as not
    repo-verifiable.
11. Run `git diff --check`.
12. Run `python3 tools/check_memory_system.py`.
13. Run any syntax/lint checks for touched scripts.
14. Commit and record the maintenance change in `CHANGELOG.md`.

## Handoff Limit

Keep `AGENT_HANDOFF.md` small (the checker hard-caps it at 120 lines). Keep it to
the standard `## Active State Summary` section. It must not contain:

- `Latest Completed` or `Changelog` sections;
- extra topical headings for follow-ups, completed work, or deploys;
- completed task history;
- long verification logs;
- broad durable rules that belong in topic memory or runbooks.

## Plans And History

`docs/plans/` must stay resumable. If a plan is complete, retired, or useful only
as historical background, move it to `docs/site_history/` and promote any
still-current rules into the relevant `docs/memory/<topic>.md` file.

The committed pre-commit hook runs `tools/check_memory_system.py` and fails when
the handoff grows past the hard limit or required memory/runbook files disappear.

## Validator Guardrails

`tools/check_memory_system.py` also enforces:

- `PROJECT_MEMORY.md` must route every topic memory file.
- `docs/plans/README.md` must index every active plan file.
- Topic memory files must keep the standard section set.
- Dated current facts must use `Last verified YYYY-MM-DD`.
- `AGENTS.md` and `CLAUDE.md` must stay byte-identical.
