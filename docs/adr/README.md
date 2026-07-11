# Architecture Decision Records (ADR)

アーキテクチャ上の重要な決定を記録する場所。フォーマットは
[MADR](https://adr.github.io/madr/) をベースにする。

## なぜ ADR か

- 「なぜこの設計にしたか」を決定時点の文脈ごと残す。後から理由を辿れる。
- Claude Code もこのディレクトリを参照して、確立済みの決定に沿った提案を行える。
- CLAUDE.md / `.claude/rules/` が「今守るべき規範」なのに対し、ADR は
  「その規範に至った決定と背景」を保存する。

## current / archive の使い分け

```
docs/adr/
├── README.md        # このファイル
├── template.md      # 新規 ADR のひな形
├── current/         # 現在有効な決定（Accepted）
└── archive/         # 覆された / 置き換えられた決定（Superseded / Deprecated）
```

- **current/** … いま有効な決定。`Status: Accepted`。
- **archive/** … 覆された決定。`Status: Superseded by ADR-XXXX` などに更新し、
  `current/` から `archive/` へ**移動**する。履歴として残し、削除しない。

## 運用ルール

1. 新しい決定は `template.md` を複製し、`current/NNNN-<slug>.md` として作成
   （`NNNN` は 4 桁連番）。
2. `Status` は `Proposed` → 合意で `Accepted`。
3. 既存の決定を覆すときは、
   - 新しい ADR を `current/` に追加し、旧 ADR を `Superseded by ADR-NNNN` に更新、
   - 旧 ADR を `archive/` へ移動する。
4. 一度作成した ADR の本文（決定当時の文脈）は書き換えず、`Status` のみ更新する。
5. `current/` に追加したら `mkdocs.yml` の `nav` にも追記する。
