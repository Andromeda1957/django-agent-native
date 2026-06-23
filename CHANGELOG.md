# Changelog

Append-only history of completed work. Newest entries on top. This file is
history; it never overrides current state (see `AGENTS.md` → Source Of Truth).

## Unreleased

- Added template operating modes: `AGENTS.md` distinguishes "building a site"
  from "maintaining the template", `docs/MAINTAINING.md` holds the maintainer
  playbook, and `/install` strips both when finalizing a clone as a real project.
- Initial django-agent-native starter: secure-by-default Django 6 project with a
  minimal demo app (`web`), the full local + CI quality-gate suite (Gitleaks,
  Ruff, import-linter, project SAST, Semgrep, pip-audit, npm audit, memory-system
  check), the agent operating contract and memory system (AGENTS/CLAUDE/GEMINI,
  runbooks, topic memory, handoff), TypeScript-by-default frontend build, and
  Claude/Codex agent wiring.
