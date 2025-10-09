#!/bin/bash
set -e

echo "📦 システムパッケージ更新..."
sudo apt-get update

echo "🐳 Docker関連パッケージをインストール..."
sudo apt-get install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg \
  lsb-release \
  python3 \
  python3-venv \
  python3-pip \
  build-essential  # n のビルドに必要

echo "🐍 Python 3.11 をインストール中..."
sudo apt-get install -y python3.11 python3.11-venv python3.11-distutils

echo "🔐 Docker GPGキーを追加..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "📂 Dockerリポジトリ追加..."
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
| sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

echo "👤 dockerグループにユーザー追加..."
sudo usermod -aG docker $USER

echo "🟢 Node.js の最新版を n でインストール中..."
curl -L https://raw.githubusercontent.com/tj/n/master/bin/n -o n
sudo bash n latest
rm n

# パス通し（bashrcに追記）
if ! grep -q 'export PATH="/usr/local/bin:$PATH"' ~/.bashrc; then
  echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
fi

export PATH="/usr/local/bin:$PATH"

echo "✅ Node.js バージョン: $(node -v)"
echo "✅ npm バージョン: $(npm -v)"

echo "📦 Poetryをインストール中..."
curl -sSL https://install.python-poetry.org | python3 -

# Poetryのパスをbashrcに追加
if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

export PATH="$HOME/.local/bin:$PATH"

echo "✅ Poetry バージョン: $(poetry --version)"

echo "インストール完了！"
echo "ターミナルを再起動、または以下を実行してください:"
echo "source ~/.bashrc"
echo "groups \$USER  # dockerグループに入っていることを確認"

echo "🐍 PoetryプロジェクトのPythonバージョンを3.11に設定中..."

# プロジェクトディレクトリ（例: ~/python）に移動する場合はここでcd
# cd ~/python

# poetry環境を3.11で作り直し（既にある場合は切り替え）
poetry env use python3.11 || poetry env use $(which python3.11)

echo "✅ 現在のPythonバージョン: $(poetry run python --version)"

echo "セットアップ完了！"
