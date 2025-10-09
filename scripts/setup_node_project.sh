#!/bin/bash
set -e

echo "🟦 Node.js プロジェクト初期化..."
npm init -y

echo "📦 devDependencies をインストール中..."
npm install --save-dev @commitlint/{cli,config-conventional} husky

echo "🛠️ commitlint 設定作成..."
cat << EOF > commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
};
EOF

echo "🐶 husky を設定中..."
# package.json の "scripts" に prepare を追加（なければ追加）
if ! grep -q '"prepare":' package.json; then
  # jqがあればそれで編集、なければ手動で注意メッセージ表示
  if command -v jq >/dev/null 2>&1; then
    jq '.scripts.prepare = "husky install"' package.json > package.tmp.json && mv package.tmp.json package.json
  else
    echo "⚠️ package.json の scripts に \"prepare\": \"husky install\" を手動で追加してください。"
  fi
fi

npm run prepare

mkdir -p .husky
echo '#!/bin/sh\nnpx --no-install commitlint --edit "$1"' > .husky/commit-msg
chmod +x .husky/commit-msg

echo "✅ husky と commitlint のセットアップが完了しました！"
