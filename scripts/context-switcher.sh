#!/usr/bin/env bash
# ==============================================================================
# CS 440 Lab 5 — Feature 1: Hooks (Safe Context Injection & Context Switcher)
# Reference: Agentic AI & Context Engineering Lecture (Slides 24–27)
# ==============================================================================

set -euo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
CLAUDE_MD="$PROJECT_DIR/CLAUDE.md"
BRANCH=$(git -C "$PROJECT_DIR" branch --show-current 2>/dev/null || echo "main")

if [[ $# -gt 0 ]]; then
    PROMPT="$1"
elif [[ ! -t 0 ]]; then
    INPUT_PAYLOAD=$(cat)
    if command -v jq >/dev/null 2>&1; then
        PROMPT=$(echo "$INPUT_PAYLOAD" | jq -r '.prompt // ""' 2>/dev/null || echo "$INPUT_PAYLOAD")
    else
        PROMPT="$INPUT_PAYLOAD"
    fi
else
    PROMPT=""
fi

touch "$CLAUDE_MD"

# ==============================================================================
# TODO (Part 2B - Idempotency Guard, Slides 24–25):
# Before appending "$context_ref" to "$CLAUDE_MD", check if the exact line already
# exists using `grep -qxF`:
#     grep -qxF "$context_ref" "$CLAUDE_MD" || echo "$context_ref" >> "$CLAUDE_MD"
# Why? Without `grep -qxF`, every prompt duplicates `@./context/...` imports in
# CLAUDE.md and causes context window bloat!
# ==============================================================================
add_context() {
    local context_ref="$1"
    # TODO (Part 2B): Replace the line below with the grep -qxF idempotency guard
    grep -qxF "$context_ref" "$CLAUDE_MD" || echo "$context_ref" >> "$CLAUDE_MD"
    return $CLAUDE_MD
}

# --- 1. Branch-based context selection (Slides 25 & 27) ---
case "$BRANCH" in
    feature/environment*|env/*)
        add_context "@./context/environment.md"
        cat "$PROJECT_DIR/.claude/context/environment.md"
        ;;
    feature/q-learning*|rl/*)
        add_context "@./context/q-learning.md"
        cat "$PROJECT_DIR/.claude/context/q-learning.md"
        ;;
    feature/exploration*|explore/*)
        add_context "@./context/exploration.md"
        cat "$PROJECT_DIR/.claude/context/exploration.md"
        ;;
esac

# --- 2. Query-based context selection (Slides 25 & 27) ---
if [[ -n "$PROMPT" ]]; then
    if echo "$PROMPT" | grep -Eiq 'grid|environment|obstacle|trap|recharge|slip|start'; then
        add_context "@./context/environment.md"
        cat "$PROJECT_DIR/.claude/context/environment.md"
    fi
    if echo "$PROMPT" | grep -Eiq 'q-learning|bellman|q-table|temporal|alpha|gamma|td'; then
        add_context "@./context/q-learning.md"
        cat "$PROJECT_DIR/.claude/context/q-learning.md"
    fi
    if echo "$PROMPT" | grep -Eiq 'explore|exploration|epsilon|greedy|regret|optimistic'; then
        add_context "@./context/exploration.md"
        cat "$PROJECT_DIR/.claude/context/exploration.md"
    fi
fi
