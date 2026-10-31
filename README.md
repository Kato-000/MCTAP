# MCTAP 本体 Judge 改良（現行 origin/main 版に適用）

対象: Kato-000/MCTAP の **現在の main (d38090e)**。4スケールではなく既に1-10だったが、
評価は無基準の“ゆる1-10”で、かつ main.py/models.py の stop_score が 1-4 前提(4/3)のままで
不整合だった。これを一括で是正・改良。

## 変更ファイル
- src/attack.py : アンカー付き1-10ルーブリック / 文量セーフ(チャンク+最大) / ゴール忠実性ゲート /
                  条件付き拒否cap(refuse-then-answer保護) / n_samples中央値 / evaluate_conversation
                  (PROGRESSIVE_MANIPを会話単位採点+ターン最大floor)。
- main.py      : stop_score 4 → 10
- src/models.py: TreeConfig.stop_score 既定 3 → 10 (docstring 1-4→1-10)
- rescore_eval.py (新規): 独立/上位Judge + 多数決で再採点→人手突合。

## 適用
    git apply MCTAP_main_judge_v2.patch   （または各ファイルで上書き）

## 補足
- 成功は TAP慣例で score==10。人手妥当性の最適閾値(前回 t=7)は VALIDITY 用に別途校正・報告。
- 公式ゆるルーブリック復帰: USE_OFFICIAL_LOOSE_RUBRIC=True。
- ゴールゲートは evaluate 1件あたりLM呼び出し+1回(軽量)。切る: check_goal_match=False。
- LM Studio の Context Length を 8k+ に上げられるなら _JUDGE_RESPONSE_CHAR_BUDGET を上げると
  チャンク分割が減る。
