#!/bin/bash
set -e

echo "🛠️ GitHub Actions ワークフローを生成中..."

mkdir -p .github/workflows

cat << 'EOF' > .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v3

      - name: 🐍 Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.14'

      - name: 🟦 Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: 📦 Install uv
        run: pip install uv

      - name: 📦 Sync Python dependencies
        run: uv sync

      - name: 📦 Install Node.js dependencies
        run: npm ci

      - name: ✅ Run Ruff (Lint)
        run: uv run ruff .

      - name: ✅ Run MyPy (Type Check)
        run: uv run mypy .

      - name: ✅ Run Tests (Pytest)
        run: uv run pytest

      - name: 🔍 Run Commitlint
        run: |
          LAST_COMMIT=$(git log -1 --pretty=%B)
          echo "$LAST_COMMIT" | npx commitlint
EOF

echo "✅ GitHub Actions の CI 設定を生成しました：.github/workflows/ci.yml"
