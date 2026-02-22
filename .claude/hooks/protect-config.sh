#!/bin/bash
# Block Claude from modifying its own configuration files.
# Used as a PreToolUse hook for Edit and Write tools.

INPUT=$(cat)
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Resolve to absolute path for consistent matching
ABS_PATH=$(realpath -m "$FILE_PATH" 2>/dev/null || echo "$FILE_PATH")
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"

# Protected paths (relative to project root)
PROTECTED=(
  "$PROJECT_DIR/CLAUDE.md"
  "$PROJECT_DIR/.claude/settings.json"
  "$PROJECT_DIR/.claude/settings.local.json"
  "$PROJECT_DIR/.claude/skills/"
  "$PROJECT_DIR/.claude/agents/"
  "$PROJECT_DIR/.claude/hooks/"
)

for PATTERN in "${PROTECTED[@]}"; do
  if [[ "$ABS_PATH" == "$PATTERN" || "$ABS_PATH" == "$PATTERN"* ]]; then
    echo "Blocked: modifying config file $FILE_PATH is not allowed. Ask the user to edit it manually." >&2
    exit 2
  fi
done

exit 0
