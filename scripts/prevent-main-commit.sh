#!/usr/bin/env bash
# ==============================================================================
# Claude Code PreToolUse Hook:
# 1. Block `git commit` on `main` / `master`
# 2. Enforce `CHANGELOG.md` staging (Keep a Changelog) before `git commit`
# ==============================================================================

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
INPUT_PAYLOAD="$(cat || true)"

if echo "$INPUT_PAYLOAD" | grep -Eq 'git[[:space:]]+commit'; then
    BRANCH="$(git -C "$PROJECT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"
    if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
        echo "BLOCKED [PreToolUse Hook]: Never commit directly to '$BRANCH'. Create a feature branch first (e.g., git checkout -b feature/q-learning)." >&2
        exit 2
    fi

    if ! git -C "$PROJECT_DIR" diff --cached --name-only | grep -qx "CHANGELOG.md"; then
        echo "BLOCKED [PreToolUse Hook]: CHANGELOG.md must be updated (Keep a Changelog format) and staged before committing. Run: bash scripts/changelog-add.sh Added|Changed|Fixed \"entry\"" >&2
        exit 2
    fi
fi
