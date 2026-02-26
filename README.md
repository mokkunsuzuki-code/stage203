# Stage201: PoC設計書（内部文書）

このフォルダは **実証（PoC）を“運用設計”として定義するための内部文書＋最小ランタイム雛形**です。
外部公開用ではありません。

## 目的
- 実証環境想定（QKD or Hybrid）
- 運用プロファイル
- 障害時挙動（Fail-Closed / Fallback）
- ログ取得方法
- 評価指標

## 主要ドキュメント
- `poc_design.md`：PoC設計書（本文）
- `profiles/`：運用プロファイル（YAML）
- `failure_models/`：障害／攻撃シナリオ定義
- `logging/`：ログ仕様（schema含む）
- `metrics/`：評価指標
- `integration/`：Stage191（CI/Claim）との接続仕様

## 出力（git管理外）
- `out/poc_logs/`：PoC実行ログ置き場（`.gitignore`で除外）

## ライセンス
- MIT License © 2025 Motohiro Suzuki
