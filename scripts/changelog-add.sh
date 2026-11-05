#!/usr/bin/env bash
# ==============================================================================
# Keep a Changelog Helper Script: scripts/changelog-add.sh
# Usage:
#   bash scripts/changelog-add.sh <Added|Changed|Deprecated|Removed|Fixed|Security> "Your changelog entry"
# ==============================================================================

set -euo pipefail

if [[ $# -lt 2 ]]; then
    echo "Usage: bash scripts/changelog-add.sh <Added|Changed|Fixed|Removed> \"Description of change\"" >&2
    exit 1
fi

SECTION="$1"
 shift
ENTRY="$*"

case "$SECTION" in
    Added|Changed|Deprecated|Removed|Fixed|Security)
        ;;
    *)
        echo "ERROR: Invalid Keep a Changelog section '$SECTION'." >&2
        echo "Valid sections: Added, Changed, Deprecated, Removed, Fixed, Security" >&2
        exit 1
        ;;
esac

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHANGELOG_FILE="$REPO_ROOT/CHANGELOG.md"

python3 - "$CHANGELOG_FILE" "$SECTION" "$ENTRY" <<'PY'
import sys
from pathlib import Path

changelog_path = Path(sys.argv[1])
section = sys.argv[2]
entry = sys.argv[3].strip()

text = changelog_path.read_text(encoding="utf-8")
bullet = f"- {entry}"

if bullet in text:
    print(f"Entry already present in {changelog_path.name}.")
    sys.exit(0)

unreleased_header = "## [Unreleased]"
section_header = f"### {section}"

if unreleased_header not in text:
    raise SystemExit("ERROR: '## [Unreleased]' section missing from CHANGELOG.md")

before_unreleased, after_unreleased = text.split(unreleased_header, 1)

# Split at next version header (if any) so we only search inside [Unreleased]
next_ver_idx = after_unreleased.find("\n## [")
if next_ver_idx != -1:
    unreleased_body = after_unreleased[:next_ver_idx]
    rest_versions = after_unreleased[next_ver_idx:]
else:
    unreleased_body = after_unreleased
    rest_versions = ""

if section_header in unreleased_body:
    sec_before, sec_after = unreleased_body.split(section_header, 1)
    updated_unreleased = f"{sec_before}{section_header}\n{bullet}{sec_after}"
else:
    updated_unreleased = f"\n\n{section_header}\n{bullet}{unreleased_body}"

changelog_path.write_text(
    f"{before_unreleased}{unreleased_header}{updated_unreleased}{rest_versions}",
    encoding="utf-8",
)
print(f"Added under {unreleased_header} -> {section_header}: {bullet}")
PY

git -C "$REPO_ROOT" add "$CHANGELOG_FILE"
echo "Staged CHANGELOG.md."
