# Maintaining django-agent-ready-template

Read this when you are working on **the template itself** (the upstream
`django-agent-ready-template` source), not on a site built from it. If
`/install` has run and `origin` is your own project repo, you are NOT in this
mode — ignore this file (a built project deletes it during `/install`).

Everything you change here propagates to everyone who clones the template. The
template's value is that it stays generic, secure, and coherent. Maintain that.

## What this template is

A secure-by-default, AI-agent-ready Django template. The differentiator is the
**agent operating system** (contract, runbooks, memory system, enforcement
gates), not the Django boilerplate. The example `web` app is throwaway scaffolding
that exists only to exercise the gates on a fresh clone.

## Core design principles (do not erode)

- **Two gradients.** Opt-*out* for things on by default because they are simply
  better (TypeScript, strict mode, the gates, the memory system). Opt-*in* for
  features that add attack surface (accounts, 2FA, REST API). Never flip a
  feature that adds attack surface to on-by-default.
- **Keep risk-bearing features opt-in, not bundled; harden everything that does
  ship by default.**
- **Generic only.** No domain/business logic in the base. If something survives
  only because of a specific use case, it does not belong in the template.
- **Enforcement over intention.** Rules that matter are gates
  (`tools/check_*.py`, CI, hooks), not just prose. If you add a durable rule,
  back it with a check where practical.

## Multi-agent model

- `AGENTS.md` is canonical. `CLAUDE.md` is a byte-for-byte mirror — never edit it
  directly; edit `AGENTS.md` and run `python3 tools/sync_agents.py`.
- `GEMINI.md` is a read-only overlay, not a mirror.
- Skills are intentionally per-agent (`.claude/skills/`, `.agents/skills/`) so
  each agent is used for its strengths. Only `/install` must exist in every
  first-class agent format. Do not build machinery to mirror all skills across
  agents — that fights how multi-agent setups are actually used.

## How to change things safely

- **Edit the contract:** change `AGENTS.md`, run `tools/sync_agents.py`, run
  `tools/check_memory_system.py`. The checker asserts specific phrases/shape —
  keep them or update the checker deliberately.
- **Add a runbook:** add `docs/runbooks/<name>.md`, list it in the runbooks
  `README.md` and `AGENTS.md`, and add it to `REQUIRED_FILES` in
  `tools/check_memory_system.py` if it should be mandatory.
- **Add a topic memory file:** use the standard five-section shape (Current
  Setup, Current Rules, Runbooks, Lookup Anchors, Deprecated / Historical), and
  route it from `PROJECT_MEMORY.md` (the checker enforces routing).
- **Add a gate:** wire it into `hooks/pre-commit` and `.github/workflows/ci.yml`,
  and into `tools/check_memory_system.py`'s required-locations checks if it must
  always run.
- **Add a Django app to the example:** keep it minimal and generic; register it
  in `INSTALLED_APPS`, `SCAN_ROOTS` (`tools/check_security_patterns.py`), and the
  `deploy.sh` tar allowlist.

## Before you commit

Run the full local gate suite (this is what a fresh clone must pass):

```bash
ruff check .
lint-imports
python3 tools/check_security_patterns.py
python3 tools/check_memory_system.py
python3 manage.py test web
npm run typecheck && npm run build:js
git diff --exit-code -- static/web/js
python3 tools/sync_agents.py --check
```

Update `CHANGELOG.md`. Refresh `constraints.txt` when Python dependencies
change. Keep `AGENT_HANDOFF.md` to current state only.

## Releasing

This is a snapshot template (consumers fork/"Use this template"); there is no
upgrade channel back into existing clones. Keep dependency pins current via
Dependabot, and treat `main` as always-clonable.
