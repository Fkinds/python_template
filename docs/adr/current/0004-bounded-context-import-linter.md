# ADR-0004: Bounded Context = 第一級パッケージ、境界を import-linter で強制する

- **Status**: Accepted
- **Date**: 2026-07-12
- **Deciders**: プロジェクトメンテナ

## Context（背景）

DDD を採る以上、モデルと ユビキタス言語の有効範囲（Bounded Context）を
明確に区切る必要がある。区切りが曖昧だと、ある context の語彙・エンティティが
別の context に漏れ、両者のライフサイクルが結合して壊れやすくなる。

境界を「規約」だけで守ろうとすると必ず破られる。機械的に検出・強制できる
手段が必要であり、本プロジェクトには `import-linter`（`uv run lint-imports`）
が導入済みである。

## Decision（決定）

- **第一級パッケージ 1 つを 1 つの Bounded Context とする**
  （`authors` / `books` / `notifications`）。`common` は Shared Kernel、
  `config` は配線。
- **context 間の既定関係は ACL（Anti-Corruption Layer）**とし、
  他 context の `domain/` を直接 import しない。境界は id + DTO +
  `Protocol` ポートで越える。`notifications` は常に downstream。
- **境界は `import-linter` の契約で強制する。** `pyproject.toml` に
  次を定義し、`uv run lint-imports` を必須チェックとする:
  - 各 context の **DDD レイヤ契約**（`infrastructure → interfaces →
    usecases → domain` の一方向）を `authors` / `common` /
    `notifications` に対して定義。
  - **Domain layer purity**（forbidden 契約）: `*.domain` は `django` /
    `rest_framework` / `injector` / `pydantic` / `httpx` を import 不可。
- **`books` は YAGNI の意図的な例外**: フルレイヤ化せず、import-linter
  契約も持たない単純 CRUD とする。フルレイヤ／契約の期待は `authors` /
  `notifications` / `common` に適用する。

## Considered options（検討した選択肢）

- 境界はコードレビューと規約のみで守る — 破られても検出できず、じわじわと
  結合が進むため却下。
- 全パッケージを一律フルレイヤ + 契約化する（`books` も含む）— 単純 CRUD に
  レイヤと契約を課すのは YAGNI 違反で過剰なため却下。
- （採用）**1 パッケージ = 1 BC、import-linter でレイヤ + domain 純度を
  機械強制、`books` は明示的例外** — 強制力と現実的コストを両立。

## Consequences（結果・トレードオフ）

- Positive: 層の逆流・domain 層への外部依存混入が CI で機械的に落ちる。
  境界侵犯が「提案」ではなく「エラー」になる。
- Positive: context 内では語彙が 1 意味に保たれ、context 間の語の相違は
  そのまま許容できる（`books` の Book ≠ `notifications` の Book 参照）。
- Negative: context を跨ぐ連携に id + DTO + ACL ポートの一手間がかかる。
- Follow-up: 現状の契約は「per-context DDD layers + domain purity」であり、
  「他 context の `domain/` を import しない」独立性は主に レイヤ + 純度契約と
  レビューで担保している。明示的な cross-context independence 契約が必要に
  なれば追加する。詳細は `.claude/rules/ddd-context-boundary-design.md` /
  `.claude/rules/ddd-architecture.md`。
