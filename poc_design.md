# Stage201 PoC設計書（内部文書）

## 1. 実証環境想定
- QKD統合（Strict）
- Hybrid（PQC + classical fallback）

## 2. 運用プロファイル
- Profile-QKD-Strict
- Profile-Hybrid-Balanced
- Profile-Resilience-Test

## 3. 障害時挙動
- QKD取得失敗
- downgrade検知
- replay検知
- rekey race

## 4. ログ取得方法
- 取得対象（鍵そのものは保存しない）
- 保存先：out/poc_logs/
- フォーマット：JSON Lines推奨

## 5. 評価指標
- Security
- Availability
- Performance
- Claim整合性（Stage191 CI run IDと結び付ける）

## 6. 成功定義（Completion Criteria）
