# project-init（スキル配布リポジトリ）

このリポジトリは Claude Code 用スキル `/project-init` そのもの。アプリケーションのコードはない。ルートの `SKILL.md` がスキル本体で、`.claude-plugin/plugin.json` が `skills: ["./"]` でルートをスキルとして読ませている。同じディレクトリが「個人スキル（~/.claude/skills に clone）」「プラグイン」「マーケットプレイス」の 3 つを兼ねる。要件は `docs/requirements.md`。

## 構成

- `SKILL.md` — スキル本体。フェーズ①〜⑤の手順。frontmatter の `name` は `project-init` 固定、`description` は 1024 文字以内
- `references/` — `questions.md`（質問リスト）、`review-lenses.md`（レビュー観点）、`scaffold-guide.md`（生成物のテンプレート）。SKILL.md から相対パスで参照される
- `scripts/scaffold.py`、`assets/manifest.example.json` — スキルの一部として配布される
- `.claude-plugin/` — `plugin.json` と `marketplace.json`。**両方の `version` を常に同じ値にする**
- 配布物に含めないもの: `tools/`（検証・パッケージ化）、`docs/`、`.claude/`（このファイル、settings、hooks、リポジトリ専用スキル）、`README.md`、`.github/`。CLAUDE.md をルートに置くと `claude plugin validate --strict` が警告するため `.claude/` 配下に置いている
- `.claude/skills/update-watch/` — Claude Code の更新を検知して修正案を Issue にする。`docs/update-watch/baseline.md` と `snapshots/` が比較の基準
- `.claude/skills/pre-pr-check/` — PR 前の検証と自己レビュー文の生成

## 編集の方針

- スキルの挙動を変えるときは `SKILL.md` と `references/` を直す。README には手順を書かない（手順の正は SKILL.md）
- `SKILL.md` の frontmatter `description` はトリガー条件そのもの。変えたら README の冒頭と `plugin.json` の `description` も合わせる
- `references/` のセクション番号（§1-1 など）は `SKILL.md` と `review-lenses.md` から参照されているので、番号を変えたら参照元も直す
- `references/scaffold-guide.md` の「要確認」項目は `docs/update-watch/baseline.md` の要確認リストと対応させる。確定したら両方を更新する
- ファイル名・識別子は英語、本文は日本語

## 完了の定義（検証）

- 変更が「動いた」と言えるのは `/pre-pr-check` の検証コマンド 3 本（`tools/package.py --check`、plugin.json と marketplace.json の `claude plugin validate --strict`）が通ったとき。`scripts/scaffold.py` を触ったら `tools/smoke_scaffold.py` も
- 配布物（SKILL.md、references/、scripts/、assets/）を変えたら、`claude --plugin-dir .` で起動して `/pre-pr-check` が示す手動シナリオ（S1〜S3）のうち関係するものを流す。自動化はしない
- レビュー: PR 本文に `/pre-pr-check` の自己レビュー文（影響フェーズ・参照 §番号・賞味期限行）を載せてから、人が差分を見てマージする
- フィードバック: 使っていて気づいた不満・改善点は GitHub Issues に溜める。`/update-watch` を回すときに open Issue も一緒に見る

## Git

- コミットは自由。**push は確認を取る**（settings.json で ask）。force push はしない（deny） — 理由: 配布中のブランチとタグを壊さないため
- Issue／PR の作成は確認不要
- 自動実行（Routine、hook）は読み取りと Issue 作成まで。ベースラインの更新は人が `fetch.py --baseline` で行う

## リリース

1. `plugin.json` と `marketplace.json` の `version` を同じ値に上げてコミット
2. `claude plugin tag --push`（`project-init--v<version>` タグを作成・push。確認あり）
3. `Release` ワークフローが `.skill` と plugin zip を添付した GitHub Release を作る
4. claude.ai に同期しているスキルは `.skill` を手動で再アップロードする
