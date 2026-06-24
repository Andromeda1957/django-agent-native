# Project Memory

This file is the memory router. It is intentionally short. Use it to choose the
right runbook and topic memory file; do not turn it back into a project
encyclopedia.

## Source Layers

- Agent behavior: `AGENTS.md`.
- Required workflows: `docs/runbooks/`.
- Active state: `AGENT_HANDOFF.md`.
- Current durable facts: `docs/memory/`.
- Deferred implementation plans: `docs/plans/`.
- Historical audit trail: `CHANGELOG.md`.
- Archived context and retired plans: `docs/site_history/`.

## Topic Index

- Workflow and memory system: `docs/memory/workflow.md`
- Deployment, backup, and local checks: `docs/memory/deployment.md`
- Production infrastructure and operations: `docs/memory/production.md`
- Frontend, templates, and UI verification: `docs/memory/frontend.md`
- TypeScript build and client-code conventions: `docs/memory/typescript.md`
- Security, privacy, and the security gate: `docs/memory/security.md`
- Code organization and architecture boundaries: `docs/memory/architecture.md`

## Lookup Rules

- Read `AGENT_HANDOFF.md` for active work and live job state.
- Read only the topic file(s) relevant to the user's request.
- Read `docs/plans/` only when the request, handoff, or a topic memory file
  routes to a specific plan.
- Use search and code/config inspection for implementation truth.
- Use `CHANGELOG.md` only for history, audit, or when a topic file points there.
- Use `docs/site_history/` only for archived context, retired plans, audit, or
  when a current memory file points to a specific historical entry.
- Treat `Deprecated / Historical` sections as non-operative.

## Global Current Facts

- This is a Django 6 project: app code under `web/`, settings under `config/`,
  templates under `web/templates/web/`, source static assets under
  `static/web/`, and TypeScript under `static/web/ts/` compiled to
  `static/web/js/`.
- Local development uses SQLite with zero setup; production uses PostgreSQL via
  `DATABASE_URL`.
- `DEBUG` defaults to False (secure by default). Production requires `SECRET_KEY`
  and `ALLOWED_HOSTS`.
- Secrets stay out of the repo: use `.env` locally (git-ignored) and real
  environment variables / secret stores in production.
- Current active work, if any, is in `AGENT_HANDOFF.md`.
