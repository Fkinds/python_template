# fkinds-python docs

Django REST Framework API テンプレートのドキュメントサイトです。

このサイトは [MkDocs](https://www.mkdocs.org/) +
[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) で
生成しています。メニュー（目次）は `mkdocs.yml` の `nav` で管理します。

## ローカルでの起動

```bash
# ライブリロード付きの開発サーバー
uv run mkdocs serve

# 静的サイトを site/ にビルド
uv run mkdocs build
```

## 構成

- `mkdocs.yml` — サイト設定とメニュー（`nav`）
- `docs/` — Markdown ドキュメント
- `site/` — ビルド成果物（gitignore 済み）
