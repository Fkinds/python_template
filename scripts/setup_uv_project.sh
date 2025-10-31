#!/bin/bash
set -e

# プロジェクト名と仮想環境名
PROJECT_NAME="my-project"
VENV_NAME="myenv"
PYTHON_VERSION="3.14.0"


echo "🐍 Python 3.14.0 を uv でインストール中..."
uv python install $PYTHON_VERSION

echo "🛠 仮想環境 $VENV_NAME を作成中..."
uv venv --python $PYTHON_VERSION $VENV_NAME

echo "🔄 仮想環境を有効化..."
source $VENV_NAME/bin/activate

echo "📦 uv 用依存関係を追加中..."
uv add pytest
uv add ruff
uv add mypy
uv add pydantic
uv add fixit
uv add import-linter
uv add attrs
uv add pre-commit

echo "📄 uv.lock を生成中..."
uv lock

echo "✅ uv.lock が作成されました"

echo "🔄 仮想環境内の Python バージョン確認..."
python --version

echo "📌 使い方:"
echo "source $VENV_NAME/bin/activate  # 仮想環境有効化"
echo "uv run python  # uv 経由で Python 実行"
