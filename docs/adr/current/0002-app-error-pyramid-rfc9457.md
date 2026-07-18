# ADR-0002: 単一 AppError 例外ピラミッドと DRF EXCEPTION_HANDLER による RFC9457 マッピング

- **Status**: Accepted
- **Date**: 2026-07-12
- **Deciders**: プロジェクトメンテナ

## Context（背景）

DDD × Clean Architecture のもとで、ドメイン・usecase・interface・
infrastructure の各層がそれぞれ独自に例外を投げると、次の問題が起きる。

- どの例外がどの HTTP ステータスに対応するかが層ごとに散らばり、一貫しない。
- 5xx のときにスタックトレースや DB / スキーマ文字列がレスポンスに漏れ、
  情報漏洩の温床になる（`.claude/rules/security.md`）。
- 見落とした例外が uncaught のまま素通りしたり、逆に握り潰されたりする。

エラー表現の標準としては RFC 9457（Problem Details for HTTP APIs,
`application/problem+json`）があり、DRF は `EXCEPTION_HANDLER` という
単一の集約ポイントを提供している。

## Decision（決定）

- **すべてのアプリ例外を単一の頂点 `AppError`（`common/domain/exceptions.py`,
  stdlib のみ）から派生させた例外ピラミッドにまとめる。**
- **単一の DRF `EXCEPTION_HANDLER`（`common/infrastructure/exception_handler.py`）
  でピラミッドを RFC 9457 problem+json にマッピングする。** ここが唯一の
  情報漏洩バリアであり、素通り・握り潰しを防ぐ集約点とする。
- **エラーは「原因の所在」で親クラスを選ぶ**（不正なエンティティ →
  `EntityError`、外部サービス障害 → `AdapterError`、生成失敗 →
  `FactoryError` 等）。
- **4xx はメッセージを `detail` に出す。5xx は `detail` を空にし、
  完全なエラー + traceback はサーバ側でのみログする。**

代表的なマッピング:

| 例外 | HTTP |
|---|---|
| `EntityDoesNotExistError` | 404 |
| `EntityError`（`GenerateRepositoryError` 含む） | 422 |
| `AdapterError` | 502 |
| `FactoryError` / `RepositoryError` / 未分類 `AppError` | 500 |
| DRF `APIException` | DRF 既定に委譲 |
| 未知の `Exception` | 500（捕捉 + ログ、汎用ボディ） |

## Considered options（検討した選択肢）

- 各層でその場ごとに `Response(status=...)` を返す — マッピングが散在し、
  情報漏洩と抜け漏れを層ごとにレビューする羽目になるため却下。
- HTTP ステータスで例外を分類する（`NotFoundError` / `ServerError` …）—
  ドメイン層が HTTP を知ることになり層純度が崩れるため却下。原因の所在で
  分類する方が層の責務に沿う。
- （採用）**原因ベースの単一 `AppError` ピラミッド + 単一
  `EXCEPTION_HANDLER`** — 分類とマッピングを 1 か所に集約でき、情報漏洩
  バリアも 1 か所で担保できる。

## Consequences（結果・トレードオフ）

- Positive: HTTP マッピングと情報漏洩防止が単一の handler に集約され、
  レビュー・監査が容易。5xx で traceback / スキーマが漏れない。
- Positive: ドメイン層の例外は stdlib のみに依存し、層純度を保てる。
  attrs validator の `ValueError` / `TypeError` は interface 層で
  `serializers.ValidationError` に変換され、この方針と両立する。
- Negative: 新しい失敗モードを足すたびに「どの親クラスか（原因の所在）」を
  判断し、ピラミッドに正しく接ぐ必要がある。
- Follow-up: 詳細は `.claude/rules/exception-architecture.md`。全 base class
  は明示的に `pass` を持つ（PIE790 は無効化）。
