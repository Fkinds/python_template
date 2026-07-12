# ADR-0005: テストを Small / Medium / Large のサイズで分類する

- **Status**: Accepted
- **Date**: 2026-07-12
- **Deciders**: プロジェクトメンテナ

## Context（背景）

「unit / integration / E2E」というラベルは境界が曖昧で、人によって指す
範囲が違う。「単体テスト」と呼びながら DB に触っていたり、逆に純粋計算を
重い統合テスト扱いしたりして、遅く・不安定なテストが増える原因になる。

必要なのは、**そのテストが何に触れてよいか／どれだけ速いか**という客観的な
基準で分類し、既定を最速side に寄せることである。Google の Test Sizes が
この基準を与える。

## Decision（決定）

- **テストを「サイズ」（触れてよいもの + 速度）で分類する**。ラベル
  （unit/integration/E2E）ではなく禁止リストで判定する。

  | Size | 使ってよい | 禁止 | 時間 |
  |---|---|---|---|
  | Small | in-process のメモリ / 計算のみ | network, file I/O, DB, system clock, sleep, threads | < 100ms |
  | Medium | localhost（DB コンテナ, test HTTP server）, 一時ファイル, subprocess | 外部インターネット | < 1s |
  | Large | 何でも（実外部 API, フルスタック, ブラウザ） | — | 秒〜分 |

- **既定は Small**。clock / random / I/O は DI で注入して Small を保つ。
  Django の `TestCase` + 実 DB は Medium（フレームワーク名でなく挙動で判定）。
- **Large は per-commit で回さない**（pre-merge / nightly / pre-release）。
  遅く・不安定・非並列なので疎に保つ。
- **層とサイズの対応**を定める: `domain/` ロジック・value object と
  `usecases/`（DI で mock）は **Small**。`interfaces/repositories/`・
  API ハンドラ・migration は **Medium**。外部 API クライアント（薄い wrapper）は
  Small（HTTP を stub）+ contract test。
- **マーカー（unit / integration / functional / linting）は
  `tests/conftest.py` がテストの置き場所から自動付与する**。手で
  `@pytest.mark.*` を付けない。

## Considered options（検討した選択肢）

- unit / integration / E2E で分類する — 境界が曖昧で、DB に触る「単体」など
  誤分類を招くため却下。
- テスト戦略を定めず各自の裁量に任せる — 遅い・不安定なテストが増え、
  per-commit の実行時間が膨らむため却下。
- （採用）**Google Test Sizes（Small/Medium/Large）を禁止リストで判定し、
  既定を Small に寄せる** — 客観基準で速く安定したスイートを保てる。

## Consequences（結果・トレードオフ）

- Positive: 「DB に触る単体テスト」のような誤分類が禁止リストで排除され、
  per-commit スイートが速く安定する。
- Positive: 「domain のロジックに DB が要る」は設計の匂い（ロジックが
  repository に漏れている）と判定でき、純関数へ抽出して Small 化できる。
- Negative: Small を保つために clock / random / I/O の DI 化という設計上の
  一手間を先に払う必要がある。
- Follow-up: プロジェクト性質に応じたテストモデル（Pyramid / Trophy /
  Honeycomb）は別途選択。詳細は `.claude/rules/test-strategy.md` と
  `unit-testing-strategy` スキル。
