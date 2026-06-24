# Security & Privacy

Durable security facts and where the controls live. For implementing any change
that touches a trust boundary, follow `docs/runbooks/security-implementation.md`.

## Current Setup

- Secure-by-default settings: `DEBUG` defaults False; production security headers
  (HSTS, SSL redirect, secure cookies, nosniff, referrer policy, X-Frame-Options
  DENY) turn on automatically when `DEBUG` is False. See `config/settings.py`.
- Argon2 is the default password hasher.
- Secrets come from the environment, never the repo (`.env` is git-ignored).
- Layered security gates run in pre-commit and CI: Gitleaks (secrets), Ruff,
  `import-linter`, `tools/check_security_patterns.py` (project SAST), Semgrep
  (standard SAST), `pip-audit`, and `npm audit`.
- Python installs use pinned direct dependencies plus the checked-in
  `constraints.txt` lock/constraints file; GitHub Actions are pinned to full
  commit SHAs in CI/deploy workflows.
- Nginx rate limiting (`webapp_nginx`): a strict admin-login limiter (brute-force
  defense) and a global baseline flood limiter, keyed on client IP, returning
  429. `server_tokens off` hides the nginx version.

## Current Rules

- Never commit credentials. Never set `DEBUG=True` in production.
- Never use `|safe` or `mark_safe` on untrusted input. Rely on template
  auto-escaping (XSS defense).
- High-risk primitives (subprocess, outbound HTTP, raw SQL, dynamic execution,
  CSRF exemption, manual safe-string marking) are flagged by
  `tools/check_security_patterns.py`. Add a narrow, justified allowlist entry
  only after following the security runbook and adding a negative test.
- For each trust boundary, add a negative security test near its owning domain
  (see `web/tests/test_security.py` for the pattern).
- When you add login or public API endpoints, add matching `limit_req_zone`s in
  `webapp_nginx` (a login limiter, an API/export limiter) — see the README opt-in
  recipes. Further nginx hardening worth porting per project: a `444` scanner-trap
  location for `.env`/`.git`/`wp-*`/`*.php` probes, and a Content-Security-Policy
  header.

## Runbooks

- Security implementation gate: `docs/runbooks/security-implementation.md`.
- Deployment and recovery backup: `docs/runbooks/deploy-backup.md`.

## Lookup Anchors

- Settings: `config/settings.py`. Project SAST: `tools/check_security_patterns.py`.
- Gate config: `.gitleaks.toml`, `.semgrepignore`, CI `.github/workflows/ci.yml`.
- Example negative test: `web/tests/test_security.py`.
- Rate limiting / web-server hardening: `webapp_nginx`.

## Deprecated / Historical

- None yet. Record superseded security facts here with the date they changed.
