---
name: update-watch
description: "Claude Code の変更履歴・公式ドキュメント・モデル一覧をベースラインと比較し、project-init スキル（SKILL.md と references/）への影響箇所と修正案を Issue にまとめる。ユーザーが /update-watch と打ったとき、SessionStart hook が「Claude Code の版が上がっている」と知らせたとき、週次の Routine から呼ばれたときに使う。このリポジトリ専用で、配布物には含めない。"
disable-model-invocation: true
argument-hint: "[--no-issue]"
---

# update-watch — 更新を検知して修正案を出す

目的: Claude／Claude Code の仕様変更で `SKILL.md` と `references/` が古くなるのを、**次の実行までに気づける** ようにする。判断と取り込みは人がやる。このスキルは読み取りと Issue 作成しかしない。**push はしない。ベースラインも書き換えない**（それは人が `fetch.py --baseline` で行う）。

引数に `--no-issue` があれば Issue を作らず本文の提示だけで終える。

## 手順

1. **取得と差分**
   ```bash
   python3 .claude/skills/update-watch/scripts/fetch.py --work /tmp/update-watch
   ```
   出力の `summary.json` を読む。`errors` があれば、その取得元は「今回見られなかった」として最後の報告に残す（URL が 404 なら `docs/update-watch/baseline.md` の案内に従い `llms.txt` の目次で探し、URL の修正案を Issue に含める）。

2. **新版がなく、docs にも差分がないなら終了。** 「ベースライン X.Y.Z のまま、差分なし」と一行で報告する。Issue は立てない。

3. **CHANGELOG の読み方。** `changelog-relevant.md`（キーワードで絞った行）を先に読み、必要なら `changelog-new.md`（新しい節の全文）で前後を確認する。見るのは次の変化だけ:
   - SKILL.md / agents / rules の frontmatter フィールドの追加・廃止・改名
   - `.claude/` 配下の配置場所、`.claude-plugin/` の形式、`claude plugin` コマンド
   - `settings.json` のキー（permissions、enabledPlugins、extraKnownMarketplaces、hooks）
   - `.mcp.json` の形式と承認キー
   - モデルの追加・非推奨（`references/scaffold-guide.md` の `model:` 例と、CLAUDE.md テンプレートの賞味期限行に効く）

4. **docs の差分の読み方。** `diff/<name>.diff` を、`docs/update-watch/baseline.md` の「監視対象」表の「見るもの」に絞って読む。言い回しの変更は無視し、フィールド名・キー名・配置・コマンドの変更だけ拾う。

5. **要確認リストの点検。** `baseline.md` の「要確認リスト」で状態が「要確認」の項目を、取得した最新 docs（`/tmp/update-watch/docs/<name>.md`）で確認する。確定できたものは Issue の修正案に「scaffold-guide の該当節を書き換え、リストを確定に移す」を含める。

6. **影響箇所を特定する。** 拾った変更ごとに `SKILL.md`、`references/scaffold-guide.md`、`references/questions.md`、`references/review-lenses.md` を grep し、**ファイル:行** と、どう直すかを書く。関係する箇所がなければ「影響なし」に分類する。

7. **Issue を作る（`--no-issue` でなければ）。**
   - タイトル: `update-watch: Claude Code <最新版> までの変更の影響`（docs のみの差分なら `update-watch: docs 差分 <日付>`）
   - 重複防止: 同じタイトルの open Issue があれば作らず、その Issue に今回の差分をコメントで追記する
   - ラベル: `update-watch`（なければラベルなしでよい）
   - 作成手段: GitHub の MCP ツール（issue 作成）があればそれを使う。なければ `gh issue create`。どちらもなければ本文をそのまま出力し、「次回の手動実行で作る」と報告する
   - 本文は下の形式

8. **報告。** 最後に 3〜5 行で「新版の有無、影響ありの件数、Issue の URL（または未作成の理由）、取得できなかった元」を示す。

## Issue 本文の形式

```markdown
## 対象
- ベースライン: Claude Code <版>（<日付>）→ 最新: <版>
- docs 差分: <名前, 名前>（なければ「なし」）

## 影響あり（修正案）
| 変更 | 影響箇所 | 修正案 |
|---|---|---|
| <CHANGELOG または docs の要約> | `references/scaffold-guide.md:123` | <どう書き換えるか> |

## 影響なしと判断した変更
- <一行ずつ。後で「見落とし」か「判断済み」かを区別できるように>

## 要確認リストの点検
| # | 項目 | 結果 |
|---|---|---|

## 取り込み後にやること
1. 修正を PR にし、`/pre-pr-check` を通す
2. マージ後に `python3 .claude/skills/update-watch/scripts/fetch.py --baseline` を実行し、`docs/update-watch/` の差分をコミットする
```

## やらないこと

- `SKILL.md` や `references/` を **この場で書き換えない**。修正案は Issue に書く。書き換えは人が判断して別の作業で行う
- `docs/update-watch/baseline.md` と `snapshots/` を書き換えない
- git push、タグ作成、リリース
- 言い回しの変更や無関係な機能追加を「影響あり」に入れない。迷ったら「影響なし」に理由を添えて置く
