# project-init（スキルのソース）

このリポジトリは Claude Code スキル `project-init` そのもの。アプリではない。実装コードは `scripts/` の 2 本だけで、残りは Claude に読ませる Markdown。

## 編集時の注意
- `SKILL.md` は毎回読まれる本体。150 行以内を保つ。手順の詳細は `references/` へ逃がす。
- `SKILL.md` は `references/questions.md` の §番号（§1, §2, §3-5 等）を参照している。見出しを増減したら参照側も直す。
- `references/scaffold-guide.md` の仕様（frontmatter フィールド、CLI オプション）は公式ドキュメントで確認できたものだけ書く。未確認なら「要確認」を付け、生成物には書かせない。
- 本文は日本語、ファイル名・識別子・frontmatter は英語。`description` は二重引用符で囲む。

## 検証
- `python3 -m unittest discover -s tests` — scripts の変更時に必ず通す
- `python3 scripts/validate.py --no-tree` — SKILL.md の frontmatter 検査
- claude.ai 同期で使っている場合、ここを更新しても同期先は自動更新されない。再アップロードを案内する。
