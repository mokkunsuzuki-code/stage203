# Stage203 — External Review Open

Stage203 は外部からのレビューおよび批評を受け付けています。

本ステージは、理論的主張ではなく、
**再現可能な claim → execution → evidence 構造の確立** を目的としています。

---

## この段階で確立されるもの

- 再現可能な PoC 実行（`./run_poc.sh`）
- クレームバウンド CI 検証
- 構造化された claim → job → artifact リンク
- 機械可読な証拠ログ（`poc.jsonl`）
- fail-closed セマンティクス

---

## 非目標（Non-Goals）

Stage203 は以下を主張しません：

- 無条件 QKD セキュリティ保証
- 形式証明の完全性
- 本番環境導入の準備完了
- ネットワーク層攻撃耐性の完全性

この段階はあくまで

> 再現可能な検証構造の確立

に限定されます。

---

## 🔍 Review Thread

アーキテクチャ批評、仮定分析、攻撃拡張提案、CI検証ギャップの指摘などを歓迎します。

👉 Reviewはこちら  
https://github.com/mokkunsuzuki-code/stage203/issues/1

👉 Release  
https://github.com/mokkunsuzuki-code/stage203/releases/tag/v0.3-stage203

---

# QSP: Claim-bound, CI-verifiable session architecture

MIT License © 2025 Motohiro Suzuki

---

# 概要

Stage203 は Stage202 を外部レビュー対応の Mini-PoC にアップグレードします。

提供されるもの：

- ワンコマンド再現
- 自動証拠生成
- Claim ↔ CI job バインディング
- 機械検証可能な PoC レポート
- GitHub Actions アーティファクト出力

これは理論主張ではありません。  
これは実行拘束型の検証構造です。

---

# Quick Review（1コマンド）

```bash
INSTALL_DEPS=1 ./run_poc.sh

生成物：

out/poc_logs/poc.jsonl

out/evidence/**

out/reports/poc_report.md

これが authoritative verification path です。

CI 動作

GitHub Actions:

PoC evidence bundle 生成

job 結果取得

poc_report.md 出力

stage203-poc-report アーティファクトアップロード

CI は環境依存性排除のため stub PoC log を使用。

完全検証はローカル実行：

./run_poc.sh
Claims Structure

定義：

claims/claims.yaml

各 claim は：

required_jobs

evidence_paths

例：

claims:
  A2:
    required_jobs: ["attack_replay"]
    evidence_paths:
      - "out/evidence/attack_replay/result.txt"

Claim は execution artifact にバインドされます。

Execution Flow
Step 1 — PoC Execution

runtime/poc_runner.py

出力：

out/poc_logs/poc.jsonl

Step 2 — Attack Validation

mini_poc/poc_replay

mini_poc/poc_downgrade

mini_poc/poc_drift_injection

出力：

out/evidence/**

Step 3 — Report Generation

tools/gen_poc_report.py

出力：

out/reports/poc_report.md

Evidence Chain

PoC log 例：

{"event":"claim_gate_passed"}
{"event":"stage191_ci_summary"}

mini_poc スクリプトは：

CI job 成功確認

または claim_gate fallback

を検証します。

GitHub Actions

Workflow:
.github/workflows/stage203-ci.yml

Artifact:
stage203-poc-report

含まれるもの：

poc_report.md

claims.yaml

actions_runs.json

actions_jobs.json

out/evidence/**

out/poc_logs/poc.jsonl

Retention: 90 days

Repository Structure
stage203/
├── runtime/
├── mini_poc/
├── claims/
├── tools/
├── out/
├── .github/workflows/
├── run_poc.sh
├── requirements.txt
└── README.md
Why Stage203 Matters

外部共同研究や学術レビュー以前に必要なのは：

Claims が構造化されていること

Claims が検証可能であること

Claims がアーティファクトを生成すること

Claims が静かに劣化しないこと

Stage203 はその閾値を満たします。

License

MIT License © 2025 Motohiro Suzuki