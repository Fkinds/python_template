# fkinds-python

Django REST Framework による Web API テンプレートプロジェクト。

## 技術スタック

| カテゴリ | ツール |
|---|---|
| 言語 | Python 3.14 |
| フレームワーク | Django 5.2 / Django REST Framework 3.16 |
| データベース | PostgreSQL 16 |
| パッケージ管理 | uv |
| リンター / フォーマッター | Ruff, Fixit (カスタムルール), import-linter |
| 型チェック | MyPy (strict), ty |
| テスト | pytest, pytest-xdist, Hypothesis |
| コンテナ | Docker (マルチステージビルド) |
| CI/CD | GitHub Actions |
| Git フック | pre-commit, husky, commitlint |

## ディレクトリ構成

```
.
├── src/
│   ├── config/          # Django 設定 (settings, urls, wsgi, asgi)
│   ├── authors/         # 著者アプリ
│   └── books/           # 書籍アプリ
├── tests/
│   ├── unit/            # ユニットテスト
│   ├── functional/      # 機能テスト (DB 使用)
│   ├── integration/     # 統合テスト
│   └── linting/         # カスタムルールのテスト
├── lint_rules/          # Fixit カスタムルール
├── .github/workflows/   # CI ワークフロー
└── docker-compose.yml
```

## 環境構築

### 前提条件

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) 0.10.4+
- Docker / Docker Compose
- Node.js (commitlint 用)

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd python_template
```

### 2. 依存パッケージのインストール

```bash
uv sync --dev
```

### 3. 環境変数の設定

```bash
cp .env.example .env
```

`.env` を環境に合わせて編集する。

### 4. データベースの起動

```bash
docker compose up -d db
```

PostgreSQL 16 がポート `5432` で起動する。

### 5. マイグレーションの実行

```bash
uv run python src/manage.py migrate
```

### 6. Git フックのセットアップ

```bash
npm install
uv run pre-commit install
```

### 7. 開発サーバーの起動

```bash
uv run python src/manage.py runserver
```

`http://localhost:8000` でアクセス可能。

Docker でまとめて起動する場合:

```bash
docker compose up
```

## よく使うコマンド

### コード品質

```bash
uv run ruff check src tests        # リント
uv run ruff format src tests       # フォーマット
uv run mypy src                    # 型チェック
uv run fixit lint src tests        # カスタムルール
uv run ty check src                # 型チェック (ty)
```

### テスト

```bash
uv run pytest                              # 全テスト
uv run pytest tests/unit                   # ユニットテスト
uv run pytest tests/functional             # 機能テスト
uv run pytest tests/integration            # 統合テスト
uv run pytest tests/unit --numprocesses auto  # 並列実行
```

## Git コミット規約

[Conventional Commits](https://www.conventionalcommits.org/ja/) に準拠する。

```
<type>: <subject>
```

使用可能な type:

`feat` / `fix` / `refactor` / `test` / `chore` / `ci` / `docs` / `revert`

例:

```
feat: add user authentication endpoint
fix: resolve N+1 query in book list view
```

## CI パイプライン

GitHub Actions により、`main` ブランチへの push および Pull Request で以下が並列実行される。

| ジョブ | 内容 |
|---|---|
| ruff | リント & フォーマットチェック |
| fixit | カスタムルール検証 |
| mypy | 静的型チェック |
| ty | 型チェック |
| unit_test | ユニットテスト (並列) |
| functional_test | 機能テスト (PostgreSQL 使用、並列) |
| integration_test | 統合テスト (逐次) |
| commitlint | コミットメッセージ検証 |

## pre-commit フック

コミット時に以下が自動実行される。

1. **Ruff** - リント & フォーマット
2. **MyPy** - 型チェック
3. **Fixit** - カスタムルール
4. **pre-commit-hooks** - EOF 修正、末尾空白除去
5. **commitlint** - コミットメッセージ検証
6. **pytest** - 全テスト実行
