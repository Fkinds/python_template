# ADR-0003: 既定は Enum、StrEnum は外部ストア／ワイヤ直結ドメイン enum のみ

- **Status**: Accepted
- **Date**: 2026-07-12
- **Deciders**: プロジェクトメンテナ

## Context（背景）

列挙型の表現に `enum.Enum` と `enum.StrEnum` のどちらを既定にするかを
決める必要がある。`StrEnum` はメンバーが `str` の派生であり、そのまま
文字列として扱えて便利な一方、**メンバーが `str` そのもの**であるため、
明示の変換なしに文字列コンテキストへ暗黙に漏れ、型境界を曖昧にする。

一方、`notifications` の一部の enum（`EventType` /
`NotificationStatus` / `NotificationChannel`）は、値を
Elasticsearch の `keyword` フィールドや API の JSON へ**直接**書き出し、
その文字列から attrs `converter` で再構築する。ここでは文字列 interop が
必須要件であり、`Enum` にすると境界ごとに `.value` を足すだけで利得がない。

## Decision（決定）

- **既定は `enum.Enum`（用途特化の `IntEnum` 等を含む）とする。**
  文字列が必要な箇所は `.value` で**明示的に**変換する。
- **`enum.StrEnum` は文字列 interop が必須の場所に限定する** — すなわち
  外部 API / DB / JSON の値に直接マッチさせる必要がある場合。
- **限定的な適用例外**: メンバー文字列を外部ストア／ワイヤへ直接書き出し、
  その文字列から再構築するドメイン enum（`notifications` の `EventType` /
  `NotificationStatus` / `NotificationChannel` → Elasticsearch `keyword`
  + API JSON）は「必須 interop」に該当するため `StrEnum` を維持する。

## Considered options（検討した選択肢）

- 一律 `StrEnum` — メンバーが `str` として暗黙に漏れ、型境界が全面的に
  ぼやけるため却下。
- 一律 `Enum`（例外なし）— ES/JSON 直結の enum でも境界ごとに `.value`
  変換が増えるだけで、可読性・安全性の利得がないため却下。
- （採用）**既定 `Enum` + interop 必須箇所のみ `StrEnum`** — 型境界の
  明示性を既定で保ちつつ、外部直結の実務要件にも応える。

## Consequences（結果・トレードオフ）

- Positive: 既定で enum が `str` に暗黙変換されず、型境界が明確に保たれる。
- Positive: ES/JSON 直結 enum は `.value` 変換の定型コードを増やさずに
  シリアライズ／再構築できる。
- Negative: 「これは interop 必須か？」の判断が都度必要になる。判断基準は
  「メンバー文字列が外部ストア／ワイヤに直接出入りするか」。
- Follow-up: 詳細は `.claude/rules/python-conventions.md` §4。
