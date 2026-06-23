#!/usr/bin/env bash
set -eu

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

if ! cd "$PROJECT_DIR"; then
  printf 'Claude startup context hook could not enter project dir: %s\n' "$PROJECT_DIR"
  exit 0
fi

cat <<'EOF'
# Claude Startup Context

The following repo-backed files are injected by the project SessionStart hook.
Treat them as current startup context before any tool use.
EOF

for file in AGENTS.md AGENT_HANDOFF.md PROJECT_MEMORY.md; do
  printf '\n\n## %s\n\n' "$file"
  if [ -f "$file" ]; then
    cat "$file"
  else
    printf 'Missing required startup file: %s\n' "$file"
  fi
done

cat <<'EOF'

## Required First Step

Before any tool use:

1. Classify the user turn.
2. Select and follow the relevant `docs/runbooks/` workflow.
3. Do not report completion from code inspection alone.
EOF
