# Deploy And Backup Runbook

Use after completed website/runtime work. Replace `<owner>/<repo>` and branch
names with your own (the `/install` skill records these).

## Default GitHub Deploy

Default production deployment uses the GitHub Actions `Deploy` workflow, not a
direct local SSH deploy.

1. Run required local gates first (venv active):
   - `ruff check .`
   - `lint-imports`
   - `python3 tools/check_security_patterns.py`
   - `python3 manage.py test web`
   - `npm run typecheck`
2. Commit the completed repo change with changelog/memory/handoff updates.
3. Push your default branch to your GitHub remote.
4. Wait for CI to pass on the exact commit:

   ```bash
   gh run watch --repo <owner>/<repo> --exit-status
   ```

5. Trigger the manual deploy workflow:

   ```bash
   gh workflow run deploy.yml --repo <owner>/<repo> --ref main -f confirm=deploy
   ```

6. Watch the deploy run to completion:

   ```bash
   gh run watch --repo <owner>/<repo> --exit-status
   ```

7. Live-verify affected URLs or behavior.

## Local Fallback Deploy

Use local `./deploy.sh` only when the user explicitly requests it, GitHub Actions
is unavailable, or emergency recovery requires it. If local deploy is used, still
push the completed commit to GitHub and wait for CI unless the user explicitly
says not to push.

The GitHub `Deploy` workflow runs `./deploy.sh` after verifying the exact commit
has passing CI. It does not replace live verification. The `deploy.sh` script
runs `python3 tools/check_security_patterns.py` (among other gates) before
transferring anything to the server.

## Recovery Backup (optional)

If you keep an off-box or second-location recovery copy, sync it after live
verification. A simple pattern is an `rsync` mirror to a backup location that
excludes secrets and local state, then a commit/push of that backup repo. Record
your concrete backup target and command here once configured, and never include
`.env` or other secrets in the backup.
