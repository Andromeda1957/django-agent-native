---
name: install
description: >-
  Install and configure a fresh django-agent-native clone: set up the local
  environment, wire the GitHub repo and CI/CD, configure the deploy target, and
  validate the whole setup. Use right after cloning the template, or to re-run
  and repair a partial/interrupted install. Idempotent: safe to run again.
---

# Install django-agent-native

This skill turns a fresh clone into a working, deployable project. It is the
"installer". It is idempotent: on a re-run, detect what is already done, validate
it, and only fill gaps — do not redo settled steps or re-ask answered questions.

Do NOT ask whether to use Django, TypeScript, or the gates — those are the
template's opinionated defaults. Only collect environment-specific facts.

Collect the configuration in step 1 in one pass, then proceed through the
remaining steps without pausing for additional confirmations unless a command
fails or the user explicitly asked to review a step.

## 0. Preflight

1. Run `git status --short` and confirm this is the template clone (working
   directory is the repo root).
2. Confirm tooling: `python3 --version` (3.12+), `node --version` (22+),
   `gh auth status`. If `gh` is not authenticated, tell the user to run
   `gh auth login` and stop until done.
3. Read existing state so a re-run does not re-ask: `git remote -v`, presence of
   `.env`, `.venv`, `node_modules`, and any GitHub Actions variables
   (`gh variable list`) / secrets (`gh secret list`).

## 1. Collect configuration

Ask only for what is not already known. Mandatory now:

- **GitHub repo**: `owner/repo` (default owner = the authenticated `gh` account,
  default repo = current directory name) and visibility (public/private).

Optional now, required before first deploy (can be deferred):

- **App name** (`APP_NAME`) — used for the systemd unit and nginx file names.
  Prompt for it; if the user leaves it blank, keep the `webapp` default and skip
  the rename in step 3.
- **Deploy target**: SSH host (`REMOTE_HOST`, e.g. `root@example.com`), runtime
  user (`REMOTE_USER`), remote dir (`REMOTE_DIR`), and the production domain.

If the user is not deploying yet, do the local + GitHub setup and clearly report
that deploy config is pending.

## 2. Local environment

1. Create and populate the virtualenv:
   `python3 -m venv .venv && .venv/bin/pip install -U pip && .venv/bin/pip install -r requirements.txt -r requirements-dev.txt`.
2. `npm install`.
3. Create `.env` from `.env.example` if absent. Generate a real secret:
   `.venv/bin/python -c "from django.core.management.utils import get_random_secret_key as k; print('SECRET_KEY='+k())"` and append it to `.env`. Keep `DEBUG=True` for local.
4. Enable the git hooks: `git config core.hooksPath hooks`.
5. `.venv/bin/python manage.py migrate` and `npm run build:js`.

## 3. App naming (only if APP_NAME != webapp)

Rename the infra files and update references together so deploy stays consistent:

- `webapp.service` -> `<APP_NAME>.service`
- `webapp-health-monitor.service` / `.timer` -> `<APP_NAME>-health-monitor.*`
- `webapp_nginx` -> `<APP_NAME>_nginx`

`deploy.sh` already reads `APP_NAME` from the environment; the GitHub deploy
workflow passes it as a variable (step 4).

## 4. GitHub repo + CI/CD

1. If the repo does not exist remotely, create it:
   `gh repo create <owner>/<repo> --<public|private> --source=. --remote=origin`.
   Otherwise add/point the `origin` remote.
2. Push the default branch: `git push -u origin HEAD`.
3. Confirm CI runs and goes green:
   `gh run watch --repo <owner>/<repo> --exit-status`.
4. When deploy config is provided, set Actions variables and secrets:
   - Variables: `gh variable set APP_NAME --body "<app>"` (and `REMOTE_HOST`,
     `REMOTE_USER`, `REMOTE_DIR`).
   - Secrets: `PROD_SSH_PRIVATE_KEY` (a deploy key with access to the server) and
     `PROD_SSH_KNOWN_HOSTS` (`ssh-keyscan <host>` output). Use
     `gh secret set NAME < file`.

## 5. Validate (the install test)

Run every local gate; all must pass:

- `.venv/bin/ruff check .`
- `.venv/bin/lint-imports`
- `.venv/bin/python tools/check_security_patterns.py`
- `.venv/bin/python tools/check_memory_system.py`
- `.venv/bin/python manage.py test web`
- `npm run typecheck && npm run build:js`
- `git diff --exit-code -- static/web/js` (compiled assets current)

Then confirm remote CI is green for the pushed commit. If deploy config was set,
optionally do a first deploy via the `Deploy` workflow and live-verify.

## 6. Finalize as your project + record

- Convert the template into your project so future sessions don't treat it as the
  upstream template: remove the "Operating Modes" section from `AGENTS.md`, delete
  `docs/MAINTAINING.md`, then run `python3 tools/sync_agents.py` to refresh the
  `CLAUDE.md` mirror. (Skip if already done — this is idempotent.)
- Update `docs/memory/production.md` and `docs/memory/deployment.md` with the
  real host, domain, app name, and remote dir.
- Clear `AGENT_HANDOFF.md` to a fresh "no active work" state.
- Note the completed install in `CHANGELOG.md`.
- Tell the user what is done, what is pending (e.g. deploy config), and that they
  can now ask the agent to build their site.

## Opt-in / opt-out

- These are documented in the README, not run by this skill: removing TypeScript
  (opt-out), and adding user accounts / 2FA / a REST API (opt-in secure recipes).
  Point the user there if they ask.
