#!/usr/bin/env bash
# ==============================================================================
# Claude Code Skill Script: github-kanban-sync
# Automatically updates KANBAN_BOARD.md from pytest results and/or publishes
# GitHub Issues + a unified GitHub Project V2 Kanban board for Group 2.
# ==============================================================================

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
KANBAN_FILE="$REPO_ROOT/KANBAN_BOARD.md"
OWNER="denizin42"
REPO_WRITE="${OWNER}/cs440-lab5-strategy1-write"
REPO_ISOLATE="${OWNER}/cs440-lab5-strategy4-isolate"
PROJECT_TITLE="CS 440 Lab 5 — Group 2 Combined Kanban"

MODE="${1:---update-board}"

check_part_status() {
    local test_class="$1"
    if pytest -q -k "$test_class" "$REPO_ROOT/tests/test_lab5_progress.py" >/dev/null 2>&1; then
        echo "**Done**"
    else
        echo "**To Do**"
    fi
}

update_local_kanban_board() {
    echo "Auditing Lab 5 progress via pytest..."
    local s1 s2 s3 s4 s5
    s1=$(check_part_status "TestPart1HyperparametersInMarkdown")
    s2=$(check_part_status "TestPart2HooksAndMemory")
    s3=$(check_part_status "TestPart3Skills")
    s4=$(check_part_status "TestPart4SubAgents")
    s5=$(check_part_status "TestPart5MCP")

    python3 - "$KANBAN_FILE" "$s1" "$s2" "$s3" "$s4" "$s5" <<'PY'
import re
import sys
from pathlib import Path

kanban_path = Path(sys.argv[1])
statuses = {
    "#1": sys.argv[2],
    "#2": sys.argv[3],
    "#3": sys.argv[4],
    "#4": sys.argv[5],
    "#5": sys.argv[6],
}

text = kanban_path.read_text(encoding="utf-8")
for card_id, new_status in statuses.items():
    pattern = rf"(\|\s*\*\*{re.escape(card_id)}\*\*\s*\|.*?\|\s*)(\*\*To Do\*\*|\*\*In Progress\*\*|\*\*Done\*\*)(\s*\|)"
    text = re.sub(pattern, rf"\g<1>{new_status}\g<3>", text)

kanban_path.write_text(text, encoding="utf-8")
print(f"Updated {kanban_path}: " + ", ".join(f"{k}={v}" for k, v in statuses.items()))
PY
}

publish_github_issues_and_project() {
    if ! gh auth status >/dev/null 2>&1; then
        echo "GitHub CLI needs authentication. Running: gh auth login -h github.com -p ssh -s project,repo -w"
        gh auth login -h github.com -p ssh -s project,repo -w
    fi

    create_issue() {
        local repo="$1" title="$2" body="$3" assignee="$4"
        gh issue create --repo "$repo" --title "$title" --body "$body" --assignee "$assignee" 2>/dev/null || \
        gh issue create --repo "$repo" --title "$title" --body "$body"
    }

    echo "Creating/syncing Group 2 issues across ${REPO_WRITE} and ${REPO_ISOLATE}..."
    U1=$(create_issue "$REPO_WRITE" "[Part 1] Implement Q-Learning Hyperparameters, Epsilon-Greedy, and Bellman TD Update (src/agent.py)" "Complete Part 1A, 1B, and 1C in \`src/agent.py\`. Verify with \`pytest -v -k TestPart1QLearning\`." "denizin42")
    U2=$(create_issue "$REPO_WRITE" "[Part 2 - Strategy 1: Write] Configure UserPromptSubmit Hook, grep -qxF Guard, and Dynamic @./context Imports" "Complete Part 2A (\`.claude/settings.json\`), Part 2B (\`scripts/context-switcher.sh\`), and Part 2C (\`CLAUDE.md\`). Verify with \`pytest -v -k TestPart2HooksAndMemory\`." "chris-mills03")
    U3=$(create_issue "$REPO_WRITE" "[Part 3 - Strategy 1: Write] Complete On-Demand Q-Learning Audit Skill Frontmatter (SKILL.md)" "Complete Part 3 in \`.claude/skills/q-learning-audit/SKILL.md\`. Verify with \`pytest -v -k TestPart3Skills\`." "chris-mills03")
    U4=$(create_issue "$REPO_ISOLATE" "[Part 4 - Strategy 4: Isolate] Configure Isolated Sub-Agents (code-reviewer & researcher) and Task() Delegation" "Complete Part 4A (\`.claude/agents/*.md\`) and Part 4B (\`CLAUDE.md\`). Verify with \`pytest -v -k TestPart4SubAgents\`." "RichardsonJC")
    U5=$(create_issue "$REPO_ISOLATE" "[Part 5 - Feature 2: MCP] Implement @mcp.tool, @mcp.resource, and @mcp.prompt in mcp_server.py" "Complete Part 5A, 5B, and 5C in \`mcp_server.py\`. Verify with \`pytest -v -k TestPart5MCP\`." "denizin42")
    U6=$(create_issue "$REPO_WRITE" "[Part 6 - Submission] Sync Both Repositories & Record 3-Minute Group 2 Video Presentation" "Run full \`pytest -v\` and \`python3 -m src.q_learning\`, sync both repos, and record the 3-minute group video." "denizin42")

    if PROJECT_NUMBER=$(gh project create --owner "$OWNER" --title "$PROJECT_TITLE" --format json 2>/dev/null | jq -r '.number // empty'); then
        if [[ -n "$PROJECT_NUMBER" ]]; then
            for url in "$U1" "$U2" "$U3" "$U4" "$U5" "$U6"; do
                gh project item-add "$PROJECT_NUMBER" --owner "$OWNER" --url "$url" >/dev/null 2>&1 || true
            done
            echo "Created unified Kanban board Project #${PROJECT_NUMBER}!"
        fi
    fi
}

case "$MODE" in
    --update-board)
        update_local_kanban_board
        ;;
    --publish-github)
        update_local_kanban_board
        publish_github_issues_and_project
        ;;
    *)
        echo "Usage: $0 [--update-board | --publish-github]"
        exit 1
        ;;
esac
