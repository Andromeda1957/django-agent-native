# Changelog

Append-only history of completed work. Newest entries on top. This file is
history; it never overrides current state (see `AGENTS.md` → Source Of Truth).

## Unreleased

- Pinned runtime Python dependencies, added a checked-in `constraints.txt` for
  reproducible Python installs, routed CI/deploy/manual setup through the
  constraints workflow, pinned GitHub Actions to full commit SHAs, and updated
  manual setup to upgrade `pip` before installing/auditing dependencies.
- Added nginx rate limiting to `webapp_nginx`: a strict admin-login limiter
  (brute-force defense) and a global baseline flood limiter, keyed on client IP
  and returning 429, plus `server_tokens off`. Documented in
  `docs/memory/security.md` and referenced from the accounts/REST-API opt-in
  recipes (login + export limiters). Closes the gap where the generic config
  shipped no rate limiting despite the secure-by-default posture.
- Added template operating modes: `AGENTS.md` distinguishes "building a site"
  from "maintaining the template", `docs/MAINTAINING.md` holds the maintainer
  playbook, and `/install` strips both when finalizing a clone as a real project.
- Initial django-agent-native starter: secure-by-default Django 6 project with a
  minimal demo app (`web`), the full local + CI quality-gate suite (Gitleaks,
  Ruff, import-linter, project SAST, Semgrep, pip-audit, npm audit, memory-system
  check), the agent operating contract and memory system (AGENTS/CLAUDE/GEMINI,
  runbooks, topic memory, handoff), TypeScript-by-default frontend build, and
  Claude/Codex agent wiring.
