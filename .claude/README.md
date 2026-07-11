# `.claude/` ガイダンス構成インデックス

このディレクトリは Claude Code へのプロジェクト固有ガイダンスを収める。
ガイダンスは **3 層** で構成し、それぞれ役割が異なる（新しいコーディング
標準を足すときは 3 層すべてに反映する）:

| 層 | 場所 | 役割 |
|---|---|---|
| **rules**（強制される既定） | `.claude/rules/*.md` | プロジェクトの MUST。CLAUDE.md から参照され、常にプロジェクト指示として読み込まれる |
| **skills**（用例集 / 手順） | `.claude/skills/*/SKILL.md` | rule を深掘りする例・チェックリスト・実行手順。必要時に呼び出される |
| **code-reviewer**（レビュー観点） | `.claude/agents/code-reviewer.md` | rules を 1 本のレビューチェックリストに落とし込んだサブエージェント |

- **rules = 何を守るか**、**skills = どう守るか（例・手順）**、
  **code-reviewer = 守れているかの点検**、という関係。
- CLAUDE.md は最上位の要約であり、詳細は rules に委譲する。

## Rules（`.claude/rules/`）

| ファイル | 概要 | 関連 skill |
|---|---|---|
| `workflow.md` | 作業の進め方（plan mode 既定、subagent 活用、検証してから完了、自己改善ループ） | — |
| `python-conventions.md` | 横断的 Python 規約（不変オブジェクト、set/frozenset、iterator、Enum、命名） | `code-quality`, `unit-testing-strategy` |
| `ddd-architecture.md` | DDD × Clean Architecture のレイヤ構造と依存方向、ライブラリ対応 | `design-patterns` |
| `ddd-domain-design.md` | ドメインオブジェクトの完全性（always-valid、Entity/VO、集約、貧血症禁止） | `design-patterns` |
| `ddd-context-boundary-design.md` | Bounded Context の境界（他 context の domain を import しない、ACL） | `design-patterns` |
| `exception-architecture.md` | `AppError` 例外ピラミッドと DRF EXCEPTION_HANDLER の RFC9457 マッピング | — |
| `security.md` | 境界での検証、情報漏洩防止、serializer 最小公開、本番ハードニング | `security` |
| `test-strategy.md` | テストサイズ（Small/Medium/Large）とテストモデル（**サイズ定義の canonical**） | `unit-testing-strategy` |

## Skills（`.claude/skills/`）

参照系（必要時に読むレファレンス）:

| skill | 概要 | 対応 rule |
|---|---|---|
| `code-quality` | Python コード品質の用例（引数・型・DRF serializer・例外処理） | `python-conventions.md` |
| `design-patterns` | Protocol/Adapter/Factory/Repository などパターンの適用指針 | `ddd-domain-design.md`, `ddd-context-boundary-design.md` |
| `security` | Django/DRF セキュリティチェックリスト | `security.md` §4–5 |
| `test-code-quality` | pytest のテストコード品質（AAA・命名・parametrize・fixtures・doubles） | `test-strategy.md` |
| `unit-testing-strategy` | Khorikov に基づくテスト戦略（**サイズ定義は `test-strategy.md` が canonical**） | `test-strategy.md` |

実行系（`disable-model-invocation: true`、ユーザー明示の手順実行用）:

| skill | 概要 |
|---|---|
| `lint-fix` | 全 linter/formatter を順に実行（`src tests lint_rules`、CLAUDE.md の lint チェーンと一致） |
| `run-tests` | テストスイート実行（unit / functional / integration / linting） |
| `create-migration` | Django マイグレーションの作成・適用 |

## Agent（`.claude/agents/`）

- `code-reviewer.md` — 上記 rules を 1 本のチェックリストに集約したレビュー用
  サブエージェント。コード変更後に proactively 実行する想定。

## 相互参照の原則

- **サイズ定義の正典は `rules/test-strategy.md`**。`unit-testing-strategy`
  skill はそれを前提にした深掘り reference（定義を二重管理しない）。
- rule から skill への参照は「例はこの skill」、skill から rule への参照は
  「規範はこの rule の §」という向きで書く。
- 新しい標準を追加するときは **rules に規範を書き、skills に例を足し、
  code-reviewer にチェック項目を足す**（3 層の一貫性を保つ）。
