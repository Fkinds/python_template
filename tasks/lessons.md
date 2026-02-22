# Lessons Learned

<!--
  ユーザーからの指摘や修正を記録し、同じミスを防ぐ。
  Claude がセッション中に自動更新します。
-->

## Rules Derived from Corrections

### 2026-02-22: entrypoint.sh は不要、docker-compose に直接書く

**What happened**: バケット初期化・migrate・runserver を
`scripts/entrypoint.sh` に書こうとした。
**Root cause**: 常時起動でないコマンドをエントリポイントに
含める必要はない。初回セットアップは手動実行で十分。
**Rule**: 常時実行しないコマンド（migrate, ensure_bucket 等）
はエントリポイントに含めず、手動コマンドとして提供する。
シェルスクリプトを作る前に「docker-compose の command で
済むか」「そもそも自動実行が必要か」を確認する。
**Related CLAUDE.md rule**: N/A

<!--
## Entry Template

### YYYY-MM-DD: [Brief description]

**What happened**: [What went wrong]
**Root cause**: [Why it happened]
**Rule**: [Concrete rule to prevent recurrence]
**Related CLAUDE.md rule**: [If applicable]
-->
