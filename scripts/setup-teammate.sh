#!/usr/bin/env bash
# ==============================================================================
# CS 440 Lab 5 — Group 2 Teammate Onboarding & Multi-Agent Setup Script
# Supports: Claude Code, Cursor, GitHub Copilot (VS Code), and Gemini / Antigravity
#
# Usage (inside a cloned repo):
#   bash scripts/setup-teammate.sh [--agent claude|cursor|copilot|gemini|all] [--branch feature/...]
#
# One-Liner (to clone BOTH Group 2 repos + set up everything from scratch):
#   bash scripts/setup-teammate.sh --clone-all
# ==============================================================================

set -euo pipefail

AGENT_PREF="all"
FEATURE_BRANCH=""
CLONE_ALL=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --agent)
            AGENT_PREF="${2:-all}"
            shift 2
            ;;
        --branch)
            FEATURE_BRANCH="${2:-}"
            shift 2
            ;;
        --clone-all)
            CLONE_ALL=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

if [[ "$CLONE_ALL" == "true" ]]; then
    echo "Cloning both CS 440 Lab 5 Group 2 repositories..."
    for repo in cs440-lab5-strategy1-write cs440-lab5-strategy4-isolate; do
        if [[ ! -d "$repo" ]]; then
            git clone "https://github.com/denizin42/${repo}.git" || git clone "git@github.com:denizin42/${repo}.git"
        fi
        (cd "$repo" && bash scripts/setup-teammate.sh --agent "$AGENT_PREF")
    done
    exit 0
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=============================================================================="
echo "Setting up $(basename "$REPO_ROOT") for Group 2..."
echo "=============================================================================="

# 1. Activate versioned Git hooks (blocks direct commits to main/master)
echo "[1/4] Activating Git pre-commit hook (.githooks/pre-commit -> blocks direct main commits)..."
chmod +x .githooks/pre-commit scripts/context-switcher.sh scripts/prevent-main-commit.sh \
         scripts/changelog-add.sh .claude/skills/github-kanban-sync/scripts/sync-kanban.sh
git config core.hooksPath .githooks
cp .githooks/pre-commit .git/hooks/pre-commit

# 2. Configure preferred AI Coding Agent bridges (without polluting git status)
echo "[2/4] Configuring AI Agent context bridges (--agent ${AGENT_PREF})..."
GIT_EXCLUDE="$REPO_ROOT/.git/info/exclude"
touch "$GIT_EXCLUDE"

add_git_exclude() {
    local pattern="$1"
    grep -qxF "$pattern" "$GIT_EXCLUDE" 2>/dev/null || echo "$pattern" >> "$GIT_EXCLUDE"
}

setup_cursor() {
    ln -sf CLAUDE.md "$REPO_ROOT/.cursorrules"
    mkdir -p "$REPO_ROOT/.cursor"
    ln -sf ../.mcp.json "$REPO_ROOT/.cursor/mcp.json"
    add_git_exclude ".cursorrules"
    add_git_exclude ".cursor/"
    echo "  -> Cursor configured (.cursorrules -> CLAUDE.md, .cursor/mcp.json -> .mcp.json)"
}

setup_copilot() {
    mkdir -p "$REPO_ROOT/.github"
    ln -sf ../CLAUDE.md "$REPO_ROOT/.github/copilot-instructions.md"
    add_git_exclude ".github/copilot-instructions.md"
    echo "  -> GitHub Copilot configured (.github/copilot-instructions.md -> CLAUDE.md)"
}

setup_gemini() {
    ln -sf CLAUDE.md "$REPO_ROOT/GEMINI.md"
    ln -sf CLAUDE.md "$REPO_ROOT/AGENTS.md"
    add_git_exclude "GEMINI.md"
    add_git_exclude "AGENTS.md"
    echo "  -> Gemini / Antigravity / Codex configured (GEMINI.md & AGENTS.md -> CLAUDE.md)"
}

case "$AGENT_PREF" in
    claude)
        echo "  -> Claude Code natively uses CLAUDE.md, .claude/, and .mcp.json"
        ;;
    cursor)
        setup_cursor
        ;;
    copilot)
        setup_copilot
        ;;
    gemini|agy|antigravity)
        setup_gemini
        ;;
    all|*)
        echo "  -> Claude Code natively uses CLAUDE.md, .claude/, and .mcp.json"
        setup_cursor
        setup_copilot
        setup_gemini
        ;;
esac

# 3. Verify Python + Pytest environment
echo "[3/4] Checking Python 3 & pytest environment..."
if ! python3 -m pytest --version >/dev/null 2>&1; then
    echo "  -> Installing pytest in user/virtualenv environment..."
    python3 -m pip install --quiet pytest
else
    echo "  -> $(python3 --version) and $(python3 -m pytest --version | head -n 1) ready."
fi

# 4. Optional feature branch switch + Kanban progress check
if [[ -n "$FEATURE_BRANCH" ]]; then
    echo "[4/4] Switching to feature branch: ${FEATURE_BRANCH}..."
    git checkout -B "$FEATURE_BRANCH"
else
    echo "[4/4] Current branch: $(git rev-parse --abbrev-ref HEAD) (Remember: create a feature branch before committing!)"
    echo "      Example: git checkout -b feature/q-learning"
fi

echo ""
echo "Running current Lab 5 Kanban progress check:"
bash .claude/skills/github-kanban-sync/scripts/sync-kanban.sh --update-board || true
echo "=============================================================================="
echo "Setup complete! Run 'pytest -v' to see the guided TODO test suite."
echo "=============================================================================="
