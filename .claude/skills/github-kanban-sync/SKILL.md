---
name: github-kanban-sync
description: On-demand procedural skill for synchronizing Group 2's combined Kanban board (KANBAN_BOARD.md), pytest progress status, and GitHub Issues across cs440-lab5-strategy1-write and cs440-lab5-strategy4-isolate.
---

# GitHub Issues & Combined Kanban Board Sync Skill

Load this skill whenever the user or a Group 2 teammate asks to:
- Update the combined Kanban board (`KANBAN_BOARD.md`) based on current `pytest` results
- Create or update GitHub Issues across `denizin42/cs440-lab5-strategy1-write` and `denizin42/cs440-lab5-strategy4-isolate`
- Link issues from both repositories into a unified GitHub Project V2 Kanban board

## Procedural Steps

1. **Audit Current Progress via `pytest`**:
   - Run the automated progress suite to inspect which parts (`TestPart1QLearning` through `TestPart5MCP`) are passing vs. pending:
     ```bash
     pytest -v tests/test_lab5_progress.py
     ```
2. **Update `KANBAN_BOARD.md` Card Statuses**:
   - Run the bundled skill helper script to automatically update `KANBAN_BOARD.md` statuses (`To Do` $\rightarrow$ `Done`) based on passing test classes, or to create/sync GitHub Issues and the Project V2 board:
     ```bash
     bash .claude/skills/github-kanban-sync/scripts/sync-kanban.sh --update-board
     ```
3. **Sync Issues & Unified GitHub Project V2 Board**:
   - To create/sync the 6 structured GitHub Issues across both repositories and attach them to the unified `CS 440 Lab 5 — Group 2 Combined Kanban` Project V2 board:
     ```bash
     bash .claude/skills/github-kanban-sync/scripts/sync-kanban.sh --publish-github
     ```
4. **Cross-Repository Consistency**:
   - Ensure `KANBAN_BOARD.md` is identical in both `cs440-lab5-strategy1-write` and `cs440-lab5-strategy4-isolate` before committing and pushing.
