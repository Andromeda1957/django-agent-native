# Deployment, Backup & Local Checks

How the project is built, checked, and shipped. Configure the specifics for your
own hosting via the `/install` skill.

## Current Setup

- Local quality gates run via the pre-commit hook and can be run by hand: Ruff,
  `import-linter`, `tools/check_security_patterns.py`,
  `tools/check_memory_system.py`, Django tests, TypeScript typecheck, and the
  JS build.
- CI (`.github/workflows/ci.yml`) runs the full gate sequence on push/PR.
- Production deploys default to the manual GitHub Actions `Deploy` workflow
  (`.github/workflows/deploy.yml`) after CI is green. `deploy.sh` is the
  underlying script (also usable locally for emergencies).
- Python runtime installs use `requirements.txt` plus the checked-in
  `constraints.txt`; `deploy.sh` ships both files to production.

## Current Rules

- Do not deploy a commit that has not passed CI unless it is an emergency
  recovery the user explicitly authorized.
- Keep the committed compiled JS under `static/web/js/` current; CI fails if it
  drifts from a fresh build.
- Run `collectstatic` as part of deploy; never serve with `DEBUG=True`.
- Refresh `constraints.txt` after changing Python runtime or gate dependencies.

## Runbooks

- Deployment and recovery backup: `docs/runbooks/deploy-backup.md`.
- Production operations: `docs/runbooks/production-ops.md`.

## Lookup Anchors

- Deploy script: `deploy.sh`. CI: `.github/workflows/ci.yml`. Deploy workflow:
  `.github/workflows/deploy.yml`.
- Service units: `*.service`, `*-health-monitor.*`. Web server: `*_nginx`.

## Deprecated / Historical

- None yet. Record superseded deployment facts here with the date they changed.
