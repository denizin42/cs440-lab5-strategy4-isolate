#!/usr/bin/env bash
# ==============================================================================
# CS 440 Lab 5 — 1-Second Live Demo Reset Script (Strategy 4: Isolate)
# ==============================================================================
# Resets the repository back to the clean Phase 1 starting state on `main`
# (where `src/` contains only `src/README.md` and all 11/11 Context Engineering
# pytest tests pass) so you can run a live hands-free agent demo from scratch.
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

git checkout main >/dev/null 2>&1 || true
rm -rf src/__init__.py src/environment.py src/agent.py src/q_learning.py src/__pycache__ \
       tests/test_q_learning.py EXPERIMENT_REPORT.md .context_state
git checkout -- CHANGELOG.md KANBAN_BOARD.md 2>/dev/null || true

echo "=============================================================================="
echo "CS 440 Lab 5 (Strategy 4: Isolate) — Ready for Live Agent Demo!"
echo "=============================================================================="
python3 -m pytest -q tests/test_lab5_progress.py
echo ""
echo "1. Launch your agent in this directory:"
echo "     agy          # or: claude"
echo ""
echo "2. Paste this single zero-prompt instruction:"
echo "     Solve Lab 5 autonomously end-to-end following CLAUDE.md without asking any questions."
echo "=============================================================================="
