# Documentation / Repo-Maintenance Change Runbook

Use for documentation, memory, runbook, or other repo-maintenance changes that do
not alter the running site.

## Steps

1. Read `AGENT_HANDOFF.md` and any directly relevant topic memory.
2. Make the smallest scoped change in the correct file (see
   `docs/runbooks/task-memory-triage.md` for where things belong).
3. If you edited `AGENTS.md`, run `python3 tools/sync_agents.py`.
4. Run `python3 tools/check_memory_system.py`.
5. Run `git diff --check`.
6. Update `CHANGELOG.md`.
7. Update or clear `AGENT_HANDOFF.md` if active state changed.
8. Commit, and push to your GitHub remote so CI runs.

## Notes

- Documentation-only changes do not require a production deploy unless they affect
  the running site (e.g. templates, served content).
- Do not duplicate history into `AGENT_HANDOFF.md`; that is `CHANGELOG.md`'s job.
