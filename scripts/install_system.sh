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
  build-essential \
  git \
  wget \
  libssl-dev \
  zlib1g-dev \
  libbz2-dev \
  libreadline-dev \
  libsqlite3-dev \
  llvm \
  libncurses5-dev \
  libncursesw5-dev \
  xz-utils \
  libffi-dev \
  liblzma-dev


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

# ------------------------------
# Node.js セットアップ
# ------------------------------

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

# ------------------------------
# uv セットアップ
# ------------------------------

PYTHON_VERSION="3.14.0"   # 好きなバージョンに変更可能
VENV_NAME="myenv"

echo "🐍 Python $PYTHON_VERSION を uv でインストール中..."
uv python install $PYTHON_VERSION

echo "🛠 仮想環境 $VENV_NAME を作成..."
uv venv --python $PYTHON_VERSION $VENV_NAME

echo "🔄 仮想環境を有効化..."
source myenv/bin/activate

echo "✅ 現在のPythonバージョン: $(python --version)"
echo "✅ pip バージョン: $(pip --version)"

echo "📦 Docker / Node.js / uv / Python 環境のセットアップ完了！"
echo "ターミナルを再起動、または以下を実行してください:"
echo "source ~/.bashrc"
echo "uv activate $VENV_NAME  # Python 仮想環境有効化"
echo "groups \$USER  # dockerグループに入っていることを確認"
