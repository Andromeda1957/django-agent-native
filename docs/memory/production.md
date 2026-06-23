# Production Infrastructure & Operations

Facts about the running site. Fill these in for your own deployment during
`/install` and keep them current.

## Current Setup

- Target topology (typical): a VPS / public server running the app under
  Gunicorn behind Nginx, with PostgreSQL as the database. Record your actual
  host role, domains, and service names here.
- Static files are served from `STATIC_ROOT` after `collectstatic`.
- Optional health-monitor systemd timer ships with the template; enable it in
  production if you want periodic checks.

## Current Rules

- Production runs with `DEBUG=False`, a real `SECRET_KEY`, and correct
  `ALLOWED_HOSTS`.
- Run the app as a least-privilege user; keep secrets in environment/secret
  stores, not the repo.
- Do not run heavy/long batch jobs on the web-serving process; use a separate
  worker or scheduled task.

## Runbooks

- Production operations: `docs/runbooks/production-ops.md`.
- Deployment and recovery backup: `docs/runbooks/deploy-backup.md`.

## Lookup Anchors

- Service units: `*.service`. Web server config: `*_nginx`.
- Settings: `config/settings.py`.

## Deprecated / Historical

- None yet. Record superseded production facts here with the date they changed.
