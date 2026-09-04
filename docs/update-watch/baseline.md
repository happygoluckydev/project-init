# update-watch ベースライン

`/update-watch` が比較の基準にする状態。**人が修正を取り込んだときだけ更新する**（自動実行は書き換えない）。
更新は `python3 .claude/skills/update-watch/scripts/fetch.py --baseline` で行う（下の版・日付と `snapshots/` を書き換える）。

## 最終確認

- Claude Code: 2.1.260
- 最終確認日: 2026-09-04
- モデル: Claude Fable 5.1 / Opus 5 / Sonnet 5 / Haiku 4.5 まで確認

## 監視対象

| 名前 | URL | 見るもの |
|---|---|---|
| changelog | https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md | 上の版より新しい節 |
| skills | https://code.claude.com/docs/en/skills.md | SKILL.md の frontmatter、配置場所、引数 |
| plugins | https://code.claude.com/docs/en/plugins.md | plugin.json のフィールド、レイアウト |
| plugin-marketplaces | https://code.claude.com/docs/en/plugin-marketplaces.md | marketplace.json、source の形式 |
| settings | https://code.claude.com/docs/en/settings.md | permissions、enabledPlugins、extraKnownMarketplaces |
| hooks | https://code.claude.com/docs/en/hooks.md | イベント名、stdin／stdout の形式 |
| sub-agents | https://code.claude.com/docs/en/sub-agents.md | agent の frontmatter |
| memory | https://code.claude.com/docs/en/memory.md | CLAUDE.md、`.claude/rules/`、`@path` |
| mcp | https://code.claude.com/docs/en/mcp.md | `.mcp.json` の形式、承認キー |
| claude-directory | https://code.claude.com/docs/en/claude-directory.md | `.claude/` 配下の配置一覧 |
| models | https://platform.claude.com/docs/en/models/overview.md | 新モデル、非推奨 |

URL が 404 になったら https://code.claude.com/llms.txt（Claude Code）と https://platform.claude.com/llms.txt（モデル）の目次で探し直す。

## 要確認リスト

`references/scaffold-guide.md` で「要確認」と付けた仕様。`/update-watch` はこの表を最新 docs で点検し、確定できたものは scaffold-guide を書き換えて「確定」に移す。

| # | 項目 | 該当箇所 | 出典 | 状態 |
|---|---|---|---|---|
| 1 | CLAUDE.md の `@path/to/file` 取り込みの挙動 | scaffold-guide §3 配置 | memory | 要確認 |
| 2 | `.claude-plugin/marketplace.json` の形式と `source: "./"` | scaffold-guide §6 配布 | plugin-marketplaces | **確定（2026-09-04、実機で add→install を確認）** |
| 3 | `.mcp.json` の自動承認キー `enableAllProjectMcpServers` / `enabledMcpjsonServers` | scaffold-guide §7 有効化 | settings, mcp | 要確認 |
| 4 | hooks の `$CLAUDE_FILE_PATH` 環境変数（stdin JSON の `tool_input.file_path` が確実） | scaffold-guide §8 hooks | hooks | 要確認 |
| 5 | agent frontmatter の `memory` フィールド | scaffold-guide §5 frontmatter | sub-agents | 要確認 |
| 6 | SessionStart hook の stdout が文脈に入ること | このリポジトリの hook | hooks | 確定（2026-09-04、docs で確認） |
| 7 | plugin.json の `skills: ["./"]`（ルートを単一スキルにする） | .claude-plugin/plugin.json | plugins | 確定（2026-09-04、`claude plugin init` の雛形と一致） |
