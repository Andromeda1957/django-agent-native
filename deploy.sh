#!/bin/bash
set -euo pipefail

# Production deploy script. Defaults are placeholders; the `/install` skill fills
# these in (or override via environment variables). The GitHub Actions `Deploy`
# workflow runs this script after verifying CI passed for the exact commit.
APP_NAME="${APP_NAME:-webapp}"
REMOTE_HOST="${REMOTE_HOST:-root@example.com}"
REMOTE_USER="${REMOTE_USER:-webapp_user}"
REMOTE_DIR="${REMOTE_DIR:-/home/webapp_user/app}"
ARCHIVE_PATH="${ARCHIVE_PATH:-/tmp/${APP_NAME}-project.tar.gz}"
IMPORT_LINTER_CMD="${IMPORT_LINTER_CMD:-lint-imports}"

echo "🚀 Starting deployment to $REMOTE_HOST..."

# 0. Pre-flight quality gates. Nothing ships unless ALL pass; `set -e` aborts the
#    whole deploy on the first failure, before a single file is transferred.
echo "🔎 Quality gates: ruff, import-linter, security patterns, tests..."
ruff check .
"$IMPORT_LINTER_CMD"
python3 tools/check_security_patterns.py
python3 manage.py test web
echo "✅ Gates passed — proceeding to deploy."

# 1. Transfer files. Ship only what is needed to run and configure the app.
#    DEPLOY ALLOWLIST: when you add a Django app, add it to this tar list.
echo "📦 Transferring runtime files..."
tar --exclude='__pycache__' --exclude='*.pyc' \
    --exclude='web/tests' --exclude='web/tests/*' \
    --exclude='*.swp' --exclude='*~' \
    -czf "$ARCHIVE_PATH" \
    config \
    web \
    manage.py \
    requirements.txt \
    constraints.txt \
    "${APP_NAME}.service" \
    "${APP_NAME}-health-monitor.service" \
    "${APP_NAME}-health-monitor.timer" \
    "${APP_NAME}_nginx" \
    static

scp "$ARCHIVE_PATH" "$REMOTE_HOST:/tmp/project.tar.gz"
rm "$ARCHIVE_PATH"

# 2. Remote execution
echo "⚙️  Running remote setup..."
ssh "$REMOTE_HOST" APP_NAME="$APP_NAME" REMOTE_USER="$REMOTE_USER" REMOTE_DIR="$REMOTE_DIR" 'bash -s' << 'EOF'
    set -e

    # Extract into a temporary release first so the live app directory is not
    # touched until the archive validates.
    RELEASE_DIR=$(mktemp -d /tmp/release.XXXXXX)
    tar -xzf /tmp/project.tar.gz -C "$RELEASE_DIR"

    # Refresh project files while preserving server-provisioned runtime state.
    mkdir -p "$REMOTE_DIR"
    systemctl stop "$APP_NAME" 2>/dev/null || true
    find "$REMOTE_DIR" -mindepth 1 -maxdepth 1 \
        ! -name '.env' ! -name 'venv' ! -name 'db.sqlite3' ! -name 'staticfiles' \
        -exec rm -rf {} +
    cp -r "$RELEASE_DIR"/. "$REMOTE_DIR"/
    rm -rf "$RELEASE_DIR"
    rm /tmp/project.tar.gz

    # The remote shell runs as root; hand the deployed tree to the runtime user.
    find "$REMOTE_DIR" -mindepth 1 -maxdepth 1 \
        ! -name '.env' ! -name 'venv' ! -name 'db.sqlite3' ! -name 'staticfiles' \
        -exec chown -R "$REMOTE_USER":www-data {} +

    # Production secrets must be provisioned separately from deploys.
    if [ ! -f "$REMOTE_DIR/.env" ]; then
        echo "ERROR: $REMOTE_DIR/.env is missing. Provision production secrets first."
        exit 1
    fi

    cd "$REMOTE_DIR"
    sudo -u "$REMOTE_USER" python3 -m venv venv
    sudo -u "$REMOTE_USER" venv/bin/pip install --upgrade pip
    sudo -u "$REMOTE_USER" venv/bin/pip install -r requirements.txt

    sudo -u "$REMOTE_USER" venv/bin/python manage.py migrate
    sudo -u "$REMOTE_USER" venv/bin/python manage.py collectstatic --clear --no-input

    # systemd units
    cp "$REMOTE_DIR/$APP_NAME.service" "/etc/systemd/system/$APP_NAME.service"
    cp "$REMOTE_DIR/$APP_NAME-health-monitor.service" "/etc/systemd/system/$APP_NAME-health-monitor.service"
    cp "$REMOTE_DIR/$APP_NAME-health-monitor.timer" "/etc/systemd/system/$APP_NAME-health-monitor.timer"
    systemctl daemon-reload
    systemctl enable "$APP_NAME"
    systemctl enable --now "$APP_NAME-health-monitor.timer"
    systemctl restart "$APP_NAME"

    # nginx
    cp "$REMOTE_DIR/${APP_NAME}_nginx" "/etc/nginx/sites-available/$APP_NAME"
    ln -sf "/etc/nginx/sites-available/$APP_NAME" /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    nginx -t && systemctl restart nginx
EOF

echo "✅ Deployment complete!"
