# ADR-0001: domain 層は attrs、境界 DTO は pydantic に分ける

- **Status**: Accepted
- **Date**: 2026-07-12
- **Deciders**: プロジェクトメンテナ

## Context（背景）

本プロジェクトは DDD × Clean Architecture を採用しており、`domain/` 層は
最内層で外部依存を持たない（stdlib + `attrs` のみ）ことを不変条件にしている
（`.claude/rules/ddd-architecture.md`）。

一方で、外部から入ってくる信頼できないデータや usecase 境界を越える DTO では、
型強制・スキーマ・(de)serialize が欲しくなる。この 2 つの要求を同じライブラリで
満たそうとすると、domain 層に重い依存が漏れ、レイヤ純度が崩れる恐れがある。

## Decision（決定）

- **domain 層の value object / entity / domain event は `attrs.frozen` で書く。**
- **`pydantic` は `usecases/_dto/` の境界 DTO 専用**とし、YAGNI に従い実際の
  境界が必要になったときにのみ導入する。
- HTTP 境界（request/response）は DRF serializer/deserializer のままとし、
  `pydantic` へは移行しない。

## Considered options（検討した選択肢）

- domain も含めすべて `pydantic` に統一 — domain 層に外部依存が漏れ、
  型強制で不変条件が暗黙化するため却下。
- domain も DTO も `attrs` に統一 — 境界での coercion / schema /
  (de)serialize を自前実装することになり非効率なため却下。
- （採用）**domain=attrs / DTO=pydantic の役割分担** — レイヤ純度と境界の
  堅牢性を両立できる。

## Consequences（結果・トレードオフ）

- Positive: `domain/` が base class 不要・`__slots__` + frozen で不変・
  型を暗黙 coercion しないため、不変条件が明示的に保たれる。
- Positive: 境界の untrusted input は `pydantic` の parse + validate +
  serialize を活用できる。
- Negative: ライブラリが 2 つになり、境界で attrs ↔ pydantic の変換が要る。
- Follow-up: `usecases/_dto/` は現時点で未使用。実境界が生じるまで導入しない
  （`.claude/rules/ddd-architecture.md` の YAGNI 方針に従う）。
