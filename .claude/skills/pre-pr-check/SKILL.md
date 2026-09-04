---
name: pre-pr-check
description: "project-init リポジトリの PR 前チェック。検証コマンド 3 本を実行し、手動確認シナリオ 3 本のチェックリストを提示し、PR 本文用の自己レビュー文（影響フェーズ・参照した §番号・賞味期限行）を生成する。SKILL.md や references/ を変更した後、PR を作る前、または「PR 前チェック」「自己レビュー」と言われたときに使う。"
argument-hint: "[base-branch]"
allowed-tools: Read, Grep, Glob, Bash
---

# pre-pr-check — PR 前チェックと自己レビュー

比較対象のブランチは `$0`。省略時は `main`（なければ最初のコミット）。このスキルはファイルを変更しない。

## 1. 検証コマンド（3 本とも通るまで先に進まない）

```bash
python3 tools/package.py --check
claude plugin validate --strict .claude-plugin/plugin.json
claude plugin validate --strict .claude-plugin/marketplace.json
```

`scripts/scaffold.py` に触れた変更なら、加えて `python3 tools/smoke_scaffold.py`。

失敗したら原因と修正案を示して止まる。

## 2. 差分の把握

```bash
git diff --stat <base>...HEAD
git diff <base>...HEAD -- SKILL.md references/ scripts/ assets/ .claude-plugin/
```

変更が配布物（`SKILL.md`、`references/`、`scripts/`、`assets/`、`.claude-plugin/`）に及ぶかを判定する。配布物に触れていなければ、§3 のシナリオは「不要」と明記して §4 へ進む。

## 3. 手動確認シナリオ（配布物に触れたとき）

自動化しない。ユーザーが `claude --plugin-dir .` で起動して流す。変更した箇所に関係するシナリオだけ「実施してください」と印を付けて提示する。

| # | シナリオ | 期待する振る舞い | 関係するファイル |
|---|---|---|---|
| S1 | 空のディレクトリで `/project-init 家計簿アプリ` | 現状確認のあと、①の質問が 3〜4 問で出る。引数「家計簿アプリ」が質問の前提に使われている | SKILL.md「始める前に」「①」、questions.md §1 |
| S2 | このリポジトリで `/project-init` | 観察結果が箇条書きで先に出て、最初の質問が「この理解で合っているか」 | SKILL.md「既存プロジェクトの場合」 |
| S3 | ④まで進める | レビューレポートが §C の形式で、「削る」提案が 1 件以上あり、指摘ごとに採用／不採用を選べる | SKILL.md「④」、review-lenses.md §C・§D |

`references/scaffold-guide.md` を変えたときは S3 の後に⑤まで進め、生成された frontmatter と JSON が §「生成後の検証」を通ることを確認する。

## 4. 自己レビュー文の生成

次のブロックを埋めて提示する。PR 本文にそのまま貼れる形にする。

```markdown
## 自己レビュー（pre-pr-check）
- 影響するフェーズ: <①〜⑤のうち該当するもの。なければ「配布物に変更なし」>
- 参照した §番号: <questions.md §3-5、review-lenses A-7 など。番号を変えた場合は参照元の修正も列挙>
- 賞味期限付きの行: <追加・更新・削除した `<!-- 賞味期限 -->` 行。なければ「なし」>
- description の変更: <SKILL.md の description を変えたか。変えたなら README 冒頭と plugin.json も揃えたか>
- version: <plugin.json と marketplace.json の version。リリース対象なら上げたか>
- 検証コマンド: 3 本 OK（<日時>）
- 手動シナリオ: <S1/S2/S3 のうち実施したものと結果。未実施なら理由>
```

## 5. 報告

「通った／止まった」を先頭に一行、続けて自己レビュー文、最後に「次にやること」（PR 作成、シナリオの実施、version の更新）を 2〜3 行。
