# Jailbreak Taxonomy — TAP Attack Framework

LLM の脆弱性カテゴリを体系的に分類し、TAP (Tree of Attacks with Pruning) アルゴリズムで自動的に攻撃プロンプトを生成・評価する研究フレームワーク。

---

## 目次

- [概要](#概要)
- [ディレクトリ構成](#ディレクトリ構成)
- [環境構築](#環境構築)
- [モデル設定](#モデル設定)
- [実行方法](#実行方法)
- [脆弱性カテゴリ](#脆弱性カテゴリ)
- [出力フォーマット](#出力フォーマット)
- [評価](#評価)
- [設定パラメータ](#設定パラメータ)

---

## 概要

```
Attacker LM ──→ 攻撃プロンプト生成
                    ↓
Target LM   ──→ 応答
                    ↓
Judge LM    ──→ スコア評価 (1-4)
                    ↓
Memory      ──→ 成功パターンをベクトルDB保存 → 次回の参考に
```

TAP アルゴリズムにより探索木を構築し、スコアの高いノードを優先しながら攻撃プロンプトを反復改善する。PROGRESSIVE_MANIP カテゴリはマルチターン会話を使い、ウォームアップ→エスカレーションの段階的な攻撃を行う。

---

## ディレクトリ構成

```
Resarch_LLM_Adversarial_Attack/
├── main.py                         # エントリポイント・設定
├── evaluate.py                     # 評価スクリプト (PPL / StrongREJECT)
├── src/
│   ├── attack.py                   # TAP コア (木探索・生成・評価)
│   ├── memory.py                   # RAG メモリストア (per-category .pt)
│   ├── models.py                   # データクラス・設定クラス
│   ├── vuln.py                     # 脆弱性カテゴリ定義
│   └── utils.py                    # ファイル I/O ユーティリティ
├── data/
│   ├── jailbreaks/                 # 成功した攻撃プロンプト (JSONL)
│   ├── traces/                     # 攻撃ツリーのトレース (JSON)
│   └── memory/                     # RAG ベクトルストア (.pt per category)
├── Dataset/
│   └── Original_Prompt/            # ベンチマークデータセット (JSONL)
├── logs.txt                        # 実行ログ
└── requirements.txt
```

---

## 環境構築

### 必要環境

| ツール | バージョン | 備考 |
|--------|-----------|------|
| Python | 3.10 以上 | |
| CUDA   | 11.8 以上 | GPU 使用時 (PPL 計算) |
| LM Studio | 最新版 | ローカルモデル実行 |

### インストール

```bash
# 1. リポジトリのクローン
git clone <repo_url>
cd Jailbreak_Taxonomy

# 2. 仮想環境の作成
python -m venv .venv

# Windows
.venv\Scripts\activate
# Mac / Linux
source .venv/bin/activate

# 3. 依存パッケージのインストール
pip install -r requirements.txt
```

### requirements.txt

```
# LLM / API
litellm>=1.30.0
openai>=1.0.0
anthropic>=0.25.0
huggingface_hub>=0.22.0
dspy-ai>=2.4.0

# データ処理
datasets>=2.18.0
torch>=2.1.0
jaxtyping>=0.2.28
pydantic>=2.0.0

# ユーティリティ
loguru>=0.7.0
tqdm>=4.66.0
transformers>=4.40.0   # PPL 計算 (GPT-2)
```

### LM Studio のセットアップ

1. [LM Studio](https://lmstudio.ai/) をダウンロード・インストール
2. 使用するモデルをダウンロード（推奨モデルは下記参照）
3. Local Server を起動（デフォルト: `http://localhost:1234`）
4. **Context Length を 4096 に設定**（デフォルト値、変更不要）

> **重要:** LM Studio のデフォルト Context Length は **4096 トークン**。  
> このフレームワークはこの上限を前提に `max_tokens` を動的計算しているため、  
> LM Studio 側の設定を変更した場合は `src/attack.py` の `_LM_STUDIO_CTX` も合わせて変更すること。

### 推奨モデル構成

| 役割 | 推奨モデル | 備考 |
|------|-----------|------|
| Attacker | `mistralai/Mistral-Nemo-Instruct-2407` | 指示追従が安定 |
| Target | `meta-llama/Llama-3.2-1B-Instruct` | 軽量・高速 |
| Embedding | `nomic-ai/nomic-embed-text-v1.5` | Memory 用 |
| Judge | Attacker と同じモデルで可 | |

---

## モデル設定

`main.py` の `AttackConfig` でモデルを設定する。

### A. LM Studio (ローカル)

```python
target_remote=Model(
    api_base="http://localhost:1234/v1",
    api_key="lm-studio",
    model_name="openai/llama-3.2-1b-instruct",
    temperature=0.0,
),
```

### B. Anthropic Claude API

```python
target_claude=AnthropicModel(
    model_name="claude-sonnet-4-5",
    api_key="sk-ant-...",   # または環境変数 ANTHROPIC_API_KEY
    temperature=0.0,
),
```

### C. OpenAI API

```python
target_remote=Model(
    api_base="https://api.openai.com/v1",
    api_key="sk-...",       # または環境変数 OPENAI_API_KEY
    model_name="openai/gpt-4o",
    temperature=0.0,
),
```

### D. HuggingFace Inference API

```python
target_hf=HFModel(
    model_name="meta-llama/Llama-3.3-70B-Instruct",
    api_key="hf_...",       # または環境変数 HF_TOKEN
    provider="hf-inference",
    temperature=0.0,
),
```

---

## 実行方法

### 攻撃実行

```bash
# main.py の config を設定してから実行
python main.py
```

### 評価

```bash
python evaluate.py \
    --input  data/jailbreaks/C1/memory.jsonl \
    --output data/eval/C1_results.csv \
    --api-base http://localhost:1234/v1 \
    --skip-ppl         # GPT-2 による PPL 計算をスキップ
    --skip-strongreject # StrongREJECT スコアをスキップ
```

---

## 脆弱性カテゴリ

| カテゴリ | 説明 | ターン数 |
|---------|------|---------|
| `ENC_EVASION` | ASCII / Base64 / ROT13 などのエンコーディングでフィルタ回避 | 1 |
| `DIRECT_OVERRIDE` | システムプロンプトや安全制約の直接上書き | 1 |
| `PERSONA_ROLEPLAY` | キャラクター・ペルソナ設定でアイデンティティを置換 | 1 |
| `INTENT_CONCEAL` | 正当な文脈（学術・フィクション等）で有害意図を隠蔽 | 1 |
| `PROGRESSIVE_MANIP` | 無害な会話でラポート構築後、段階的にエスカレーション | マルチターン |
| `CONTEXT_INJECTION` | 外部ソース（RAG 等）への悪意ある注入 | 1 |

各カテゴリは **4 グループ × 5 バリアント = 20 パターン** を持つ。  
木探索でグループをローテーションし、バリアントをランダムに選択することで構造的・表面的多様性を確保。

---

## 出力フォーマット

### 成功記録 (JSONL)

`data/jailbreaks/{output_name}.jsonl` に 1 行 1 レコードで保存。

```jsonc
{
  // attacker_prompt: 全ターンの会話リスト（全カテゴリ共通形式）
  "attacker_prompt": [
    {"role": "user",      "content": "ウォームアップT1"},
    {"role": "assistant", "content": "応答T1"},
    {"role": "user",      "content": "エスカレーション（最終）"},
    {"role": "assistant", "content": "成功応答"}
  ],
  "conversation":        [ /* attacker_prompt と同じ内容 */ ],
  "target_model_answer": "成功応答（最終ターン）",
  "score":               4,
  "vuln_category":       "PROGRESSIVE_MANIP",
  "goal":                "攻撃ゴール",
  "duration":            42,
  "success":             true,
  "config":              { /* AttackConfig のダンプ */ }
}
```

### トレース (JSON)

`data/traces/{goal_slug}.json` に攻撃ツリー全体を保存。

```jsonc
{
  "goal":               "攻撃ゴール",
  "success":            true,
  "duration":           42,
  "final_score":        4,
  "best_score_history": [ /* スコア改善の履歴 */ ],
  "all_attempts":       [ /* 全 Attempt レコード */ ],
  "tree":               [ /* イテレーションごとのノードツリー */ ]
}
```

### ターゲット応答 (JSONL)

`data/traces/{goal_slug}_responses.jsonl` に各ターンの応答を別ファイルで保存。  
`Attempt` オブジェクトに応答テキストを持たせないことで、TreeNode の deepcopy コストを削減。

```jsonc
{"child_id": "root",  "response": "初回応答"}
{"child_id": "1-0-2", "response": "ターゲット応答"}
```

---

## 評価

### PPL (Perplexity)

ローカルの GPT-2 を使い、攻撃プロンプトの自然言語らしさを計測。  
PPL が低いほど自然な文体（検出されにくい）。

### StrongREJECT

LM Studio 上の Judge モデルで拒否率・有害性・具体性を 0〜1 でスコアリング。

---

## 設定パラメータ

`main.py` の `AttackConfig` で設定。

| パラメータ | デフォルト | 説明 |
|-----------|-----------|------|
| `root_width` | 5 | ルートノード数（並列スタート数） |
| `depth` | 10 | 最大探索深度 |
| `branching_factor` | 3 | ノードあたりの子ノード数 |
| `width` | 10 | イテレーションごとに残すノード数 |
| `stop_score` | 4 | 成功と判定するスコア閾値 (1-4) |
| `multiturn_depth` | 3 | PROGRESSIVE_MANIP の最大エスカレーション回数 |
| `exploit_threshold` | 3 | カテゴリ継続の最低スコア |
| `patience` | 2 | カテゴリ切替までの低スコア許容回数 |
| `memory_dir` | `data/memory` | RAG ストアのディレクトリ (`None` で無効) |

---

## 注意事項

このフレームワークは **LLM の安全性研究・レッドチーミング** を目的としている。  
生成された攻撃プロンプトを実際の悪用に使用することは禁止。
