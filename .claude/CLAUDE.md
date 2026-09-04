# project-init（スキル配布リポジトリ）

このリポジトリは Claude Code 用スキル `/project-init` そのもの。アプリケーションのコードはない。ルートの `SKILL.md` がスキル本体で、`.claude-plugin/plugin.json` が `skills: ["./"]` でルートをスキルとして読ませている。同じディレクトリが「個人スキル（~/.claude/skills に clone）」「プラグイン」「マーケットプレイス」の 3 つを兼ねる。

## 構成

- `SKILL.md` — スキル本体。フェーズ①〜⑤の手順。frontmatter の `name` は `project-init` 固定、`description` は 1024 文字以内
- `references/` — `questions.md`（質問リスト）、`review-lenses.md`（レビュー観点）、`scaffold-guide.md`（生成物のテンプレート）。SKILL.md から相対パスで参照される
- `scripts/scaffold.py`、`assets/manifest.example.json` — スキルの一部として配布される
- `.claude-plugin/` — `plugin.json`（プラグイン定義）と `marketplace.json`（このリポジトリを配るマーケットプレイス）。**両方の `version` を常に同じ値にする**
- `tools/package.py` — 配布アーカイブ生成と検証。配布物には含めない
- `install.sh`、`README.md`、`.github/`、この `.claude/CLAUDE.md` — 配布物には含めない（CLAUDE.md をルートに置くと `claude plugin validate --strict` が警告するため `.claude/` 配下に置く）

## 編集の方針

- スキルの挙動を変えるときは `SKILL.md` と `references/` を直す。README には手順を書かない（手順の正は SKILL.md）
- `SKILL.md` の frontmatter `description` はトリガー条件そのもの。変えたら README の冒頭と `plugin.json` の `description` も合わせる
- `references/` のセクション番号（§1-1 など）は `SKILL.md` と `review-lenses.md` から参照されているので、番号を変えたら参照元も直す
- ファイル名・識別子は英語、本文は日本語

## 完了の定義（検証）

変更後は必ず次を通す。

```bash
python3 tools/package.py --check
claude plugin validate --strict .claude-plugin/plugin.json
claude plugin validate --strict .claude-plugin/marketplace.json
```

挙動の確認は `claude --plugin-dir .` で起動して `/project-init` を実行する。

## リリース

1. `plugin.json` と `marketplace.json` の `version` を同じ値に上げてコミット
2. `claude plugin tag --push`（`project-init--v<version>` タグを作成・push）
3. `Release` ワークフローが `.skill` と plugin zip を添付した GitHub Release を作る
