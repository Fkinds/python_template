#!/bin/bash
set -e

echo "📁 プロジェクトフォルダ初期化..."
mkdir -p src tests

echo "📦 Poetry プロジェクト初期化..."
if [ -f pyproject.toml ]; then
  echo "pyproject.toml が既に存在します。poetry init はスキップします。"
else
  read -p "プロジェクト名を入力してください: " project_name

  poetry init --no-interaction --name "$project_name" \
    --dependency django \
    --dependency pydantic \
    --dev-dependency pytest \
    --dev-dependency pytest-django \
    --dev-dependency ruff \
    --dev-dependency mypy \
    --dev-dependency drf-yasg


  echo "📦 開発パッケージ追加..."
fi
poetry add --dev pre-commit pytest ruff mypy
