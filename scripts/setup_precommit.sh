#!/bin/bash
set -e

echo "🧩 .pre-commit-config.yaml を作成中..."
cat << EOF > .pre-commit-config.yaml
repos:
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace

  - repo: local
    hooks:
      - id: pytest
        name: Run Pytest
        entry: poetry run pytest
        language: system
        types: [python]
EOF

echo "📦 pre-commit を dev-dependencies に追加..."
poetry add --dev pre-commit

echo "📦 poetry.lock を更新中..."
poetry lock

echo "📦 依存関係をインストール中..."
poetry install

echo "🔗 pre-commit をインストール＆初期化..."
git config --unset-all core.hooksPath || true
poetry run pre-commit install
