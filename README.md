# MCTAP — Memory and Category-guided Tree of Attacks with Pruning

**MCTAP** は、LLM に対するジェイルブレイク攻撃を体系的に自動生成・評価する研究フレームワークである。
「攻撃生成」「防御層に基づく脆弱性分類」「マルチターン診断フィードバック」を統合した LLM 脆弱性評価基盤であり、カテゴリ別・モデル別の脆弱性プロファイルを定量的に明示することを目的とする。

> **論文タイトル**  
> *Large Language Model に対する Jailbreak 攻撃の自動生成フレームワークと脆弱性分類の構築*

---

## 手法名について

| 略称 | 正式名称 | 意味 |
|------|---------|------|
| **MCTAP** | Memory and Category-guided Tree of Attacks with Pruning | Memory（ゴール間知識転用）× Category（防御層に基づく脆弱性分類）× TAP（幅優先探索・枝刈り）の統合 |

MCTAP は既存の TAP (Mehrotra et al., 2023) を以下の3点で拡張する。

1. **Memory 層**：過去の成功攻撃をカテゴリ別ベクトル DB に蓄積し、ゴール間で知識を転用する
2. **Category 層**：LLM の処理層（トークン・命令・役割・意図・文脈）に基づく5カテゴリの脆弱性分類を導入し、探索を構造化する
3. **マルチターン診断**：`PROGRESSIVE_MANIP` カテゴリ専用のターン単位診断フィードバック機構により、「どのターンでなぜ拒否されたか」を構造化テキストで提供する

---

## アーキテクチャ概要

```
【Memory 層】  ゴール間・長期探索
  過去成功例をカテゴリ別ベクトル DB に蓄積
  → 類似ゴールの成功プロンプトを hint として注入
        ↓
【TAP 層】     同一ゴール内・幅方向探索
  depth × root_width の探索木 + スコアによる枝刈り
  → カテゴリを適応的に選択（Exploit-Explore 制御）
        ↓
【PAIR 層】    ノード内・逐次改善
  history（過去 Attempt）を参照しながらプロンプトを反復改善

         ＋

【診断フィードバック】  PROGRESSIVE_MANIP 専用
  ウォームアップ〜エスカレーション各ターンの
  拒否パターン・失敗原因・改善指示を構造化テキストで提供
```

---

## 目次

- [実験結果](#実験結果)
- [脆弱性分類](#脆弱性分類)
- [ディレクトリ構成](#ディレクトリ構成)
- [環境構築](#環境構築)
- [モデル設定](#モデル設定)
- [実行方法](#実行方法)
- [出力フォーマット](#出力フォーマット)
- [評価指標](#評価指標)
- [設定パラメータ](#設定パラメータ)

---

## 実験結果

**ターゲットモデル**：Gemma-4-e2b、Llama-3.2-1B-Instruct、Qwen3.5-2B  
**ベンチマーク**：Cyber Attack Facilitation カテゴリ（独自作製、各カテゴリ 40 ゴール × 5 = 200 ゴール）

| モデル | カテゴリ | ASR | StrongREJECT |
|--------|---------|-----|-------------|
| Gemma-4-e2b | PROGRESSIVE_MANIP | **0.995** | 0.975 |
| Llama-3.2-1B | PROGRESSIVE_MANIP | **0.995** | 0.970 |
| Llama-3.2-1B | INTENT_CONCEAL | 0.655 | 0.985 |
| Qwen3.5-2B | PROGRESSIVE_MANIP | **1.000** | 0.980 |
| Qwen3.5-2B | DIRECT_OVERRIDE | 0.490 | 1.000 |

**主要な知見**

- `PROGRESSIVE_MANIP` は全3モデルで最高 ASR（0.995〜1.000）を達成 → マルチターン診断機構の有効性を示す
- Qwen3.5-2B は `DIRECT_OVERRIDE` のみ ASR=0.490 と突出して低い → 命令層への耐性がモデル固有に存在する
- Llama-3.2-1B は `INTENT_CONCEAL` のみ ASR=0.655 と相対的に低い → 意図層の防御が相対的に機能している

---

## 脆弱性分類

MCTAP は LLM の処理パイプラインを5層に抽象化し、各層を標的とする攻撃を1カテゴリとして定義する（**defense-layer abstraction**）。

| カテゴリ | 標的とする防御層 | ターン数 |
|---------|----------------|---------|
| `ENC_EVASION` | トークナイザー・表層キーワードフィルタ | 1 |
| `DIRECT_OVERRIDE` | システムプロンプト・優先順位制約 | 1 |
| `PERSONA_ROLEPLAY` | 自己同一性・アイデンティティ制約 | 1 |
| `INTENT_CONCEAL` | 意図分類器・文脈理解 | 1 |
| `PROGRESSIVE_MANIP` | 会話履歴の文脈依存安全評価 | マルチターン ★ |

★ `PROGRESSIVE_MANIP` のみマルチターン。ターン単位の診断フィードバック機構を適用。

各カテゴリは **4 グループ × 5 バリアント = 20 パターン**（合計 100 パターン）に細分化。
グループが構造的多様性（攻撃の骨格）、バリアントが表面的多様性（語彙・フォーマット）を担う。

---

## ディレクトリ構成

```
MCTAP/
├── main.py                         # エントリポイント・設定
├── evaluate.py                     # 評価スクリプト (ASR / StrongREJECT / Binoculars)
├── requirements.txt
├── src/
│   ├── attack.py                   # MCTAP コア（PAIR × TAP × Memory × 診断）
│   ├── memory.py                   # RAG メモリストア (per-category .pt)
│   ├── models.py                   # データクラス・設定クラス
│   ├── vuln.py                     # 脆弱性カテゴリ定義（5カテゴリ × 100 パターン）
│   └── utils.py                    # ファイル I/O ユーティリティ
├── data/
│   ├── jailbreaks/                 # 成功した攻撃記録 (JSONL)
│   ├── traces/                     # 攻撃ツリーのトレース (JSON)
│   └── memory/                     # RAG ベクトルストア (.pt per category)
├── Dataset/
│   └── Cyber_Attack_Facilitation/  # ベンチマークデータセット (JSONL)
└── logs.txt                        # 実行ログ
```

---

## 環境構築

### 必要環境

| ツール | バージョン | 備考 |
|--------|-----------|------|
| Python | 3.10 以上 | |
| CUDA | 11.8 以上 | GPU 使用時（Binoculars 計算） |
| LM Studio | 最新版 | ローカルモデル実行 |

> **重要：LM Studio の Context Length は 4096 に設定すること。**  
> MCTAP はこの上限を前提に `max_tokens` を動的計算している。  
> 変更した場合は `src/attack.py` の `_LM_STUDIO_CTX` も合わせて修正すること。

### インストール

```bash
# 1. リポジトリのクローン
git clone <repo_url>
cd MCTAP

# 2. 仮想環境の作成・有効化
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
transformers>=4.40.0   # Binoculars 計算
```

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

### A. LM Studio（ローカル）

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
# main.py の AttackConfig を設定してから実行
python main.py
```

**Resume モード（途中から再開）**  
`main.py` の `RESUME_MODE = True`（デフォルト）にすると、  
既に処理済みのゴールをスキップして未処理分のみ実行する。  
途中で落ちた場合もそのまま再実行すれば続きから始まる。

```python
RESUME_MODE = True   # 再開モード（デフォルト）
RESUME_MODE = False  # 全件最初から実行
```

### 評価

```bash
python evaluate.py \
    --input  data/jailbreaks/C1/memory.jsonl \
    --output data/eval/C1_results.csv \
    --api-base http://localhost:1234/v1
```

---

## 出力フォーマット

### 成功記録 (JSONL)

`data/jailbreaks/{output_name}.jsonl` に 1 行 1 レコードで保存。  
全カテゴリ共通で `attacker_prompt` は会話リスト形式。

```jsonc
{
  "attacker_prompt": [
    {"role": "user",      "content": "ウォームアップ T1"},
    {"role": "assistant", "content": "応答 T1"},
    {"role": "user",      "content": "エスカレーション（最終）"},
    {"role": "assistant", "content": "成功応答"}
  ],
  "conversation":        [ /* attacker_prompt と同じ内容 */ ],
  "target_model_answer": "成功応答（最終ターン）",
  "score":               4,
  "vuln_category":       "PROGRESSIVE_MANIP",
  "goal":                "攻撃ゴール",
  "duration":            42,
  "success":             true
}
```

### ターゲット応答 (JSONL)

`data/traces/{goal_slug}_responses.jsonl` に各ターンの応答を別ファイルで保存。  
`Attempt` に応答テキストを持たせないことで `TreeNode` の deepcopy コストを削減。

```jsonc
{"child_id": "root",  "response": "初回応答"}
{"child_id": "1-0-2", "response": "ターゲット応答"}
```

### エラースキップ記録

```
data/jailbreaks/{output_name}_skipped.txt
```

例外によりスキップされたゴールを記録。Resume モード再実行時に自動的に対象となる。

---

## 評価指標

| 指標 | 説明 |
|------|------|
| **ASR**（Attack Success Rate） | `stop_score ≥ 4` 到達率。LLM による有害性判定を使用 |
| **StrongREJECT** | 拒否・具体性・説得力の3次元で 0〜1 をスコアリング。ASR の過大評価を補正 |
| **Binoculars（adversarial）** | 攻撃プロンプトの自然言語らしさ。高いほど検出困難 |
| **Binoculars（original）** | 元の有害ゴールの自然言語らしさ（ベースライン） |

---

## 設定パラメータ

`main.py` の `AttackConfig` で設定。

| パラメータ | デフォルト | 説明 |
|-----------|-----------|------|
| `root_width` | 5 | ルートノード数（並列スタート数） |
| `depth` | 10 | 最大探索深度 |
| `branching_factor` | 3 | ノードあたりの子ノード数 |
| `width` | 10 | イテレーションごとに残すノード数 |
| `stop_score` | 4 | 成功と判定するスコア閾値（1〜4） |
| `multiturn_depth` | 3 | `PROGRESSIVE_MANIP` の最大エスカレーション回数 |
| `exploit_threshold` | 3 | カテゴリ継続の最低スコア |
| `patience` | 2 | カテゴリ切替までの低スコア許容回数 |
| `memory_dir` | `data/memory` | RAG ストアのディレクトリ（`None` で Memory 無効） |

---

## 参考文献

- Mehrotra et al. (2023). *Tree of Attacks: Jailbreaking Black-Box LLMs Automatically.* NeurIPS 2024. arXiv:2312.02119
- Chao et al. (2023). *Jailbreaking Black Box LLMs in Twenty Queries.* arXiv:2310.08419
- Souly et al. (2024). *A StrongREJECT for Empty Jailbreaks.* NeurIPS 2024. arXiv:2402.10260
- Hans et al. (2024). *Binoculars: Accurate Zero-Shot Detection of LLM-Generated Text.* ICML 2024.

---

## 注意事項

本フレームワークは **LLM の安全性研究・レッドチーミング** を目的としている。  
生成された攻撃プロンプトを実際の悪用に使用することは禁止する。
