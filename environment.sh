#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/scripts" && pwd)"

bash "$SCRIPT_DIR/install_system.sh"
bash "$SCRIPT_DIR/setup_uv_project.sh"
bash "$SCRIPT_DIR/setup_node_project.sh"
bash "$SCRIPT_DIR/setup_precommit.sh"
bash "$SCRIPT_DIR/generate_github_actions.sh"

echo "✅ 完了しました！ターミナルを再起動するか、以下を実行してください："
echo "  source ~/.bashrc"
echo "  groups \$USER"
