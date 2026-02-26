# ログ仕様（PoC）

## 原則
- 秘密鍵・セッション鍵など「鍵そのもの」は保存しない
- transcriptは hash化して保存
- CI run id / git commit など再現性メタ情報は必ず保存

## 出力先
- out/poc_logs/

## 推奨形式
- JSON Lines（1行1イベント）
