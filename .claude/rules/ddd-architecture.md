# DDD × Clean Architecture レイヤー構成

新規モジュールで DDD を採用する場合のレイヤー構成ガイド。

## レイヤー構成

```
module_name/
├── domain/              # 最内側: 外部依存なし
│   ├── entities/        # ドメインエンティティ
│   ├── services/        # ドメインサービス
│   └── (root modules)   # 値オブジェクト (attrs.frozen)
│
├── usecases/            # domain のみに依存
│   ├── protocols/       # ポート (typing.Protocol)
│   ├── _dto/            # データ転送オブジェクト
│   └── adapters/        # ユースケース用アダプタ
│
├── interfaces/          # 外部とのインターフェース
│   ├── serializers/
│   ├── deserializers/
│   ├── repositories/
│   ├── adapters/
│   ├── factories/
│   ├── routing/
│   └── management/commands/
│
└── infrastructure/      # 最外側: 全レイヤー参照可
    ├── containers/      # DI コンテナ (Composition Root)
    ├── adapters/        # 外部サービス実装
    └── factories/       # インフラ用ファクトリ
```

## 依存方向

```
domain ← usecases ← interfaces ← infrastructure
```

- domain: 標準ライブラリ + attrs のみ
- usecases: domain のみ import
- interfaces: domain + usecases を import
- infrastructure/adapters: Protocol を暗黙的に満たす
- infrastructure/containers: 全レイヤー参照 OK (Composition Root)

## ライブラリ使い分け

| 用途 | ライブラリ | 場所 |
|------|-----------|------|
| 値オブジェクト / ドメインイベント | `attrs.frozen` | domain/ |
| シリアライザ | `attrs` | interfaces/serializers/ |
| DTO (境界での変換) | `pydantic` | usecases/_dto/ |
| ポート | `typing.Protocol` | usecases/protocols/ |

## ルール

- YAGNI: 必要なレイヤー・ディレクトリだけ作成する
- 値オブジェクトは `attrs.frozen(kw_only=True)`
- DTO は `pydantic.BaseModel` (バリデーション + シリアライズ)
- ポートは `typing.Protocol`
- Protocol を満たす具象クラスには `*Impl` サフィックスを付ける
- ユースケース関数はキーワード引数のみ
