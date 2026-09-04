# スキャフォールドガイド — 生成物のテンプレートと Claude Code の仕様

⑤で生成する各ファイルのテンプレートと、Claude Code 側の仕様（フィールド名・配置場所）。**仕様は書いてある通りに使う。** 記憶で補完してフィールド名を捏造しない。「要確認」と付けた項目は **生成物には書かず**、ユーザーへの案内（「公式ドキュメントで確認の上、必要なら追加」）にとどめる。

目次
1. マニフェストと `scaffold.py`
2. 要件定義書 `docs/requirements.md`
3. `CLAUDE.md` と `.claude/rules/`
4. スキル `.claude/skills/<name>/SKILL.md`
5. サブエージェント `.claude/agents/<name>.md`
6. プラグイン `.claude-plugin/`
7. MCP `.mcp.json`
8. `.claude/settings.json` と hooks
9. `.gitignore` / `.env.example`
10. 生成後のユーザー向け案内

---

## 1. マニフェストと `scaffold.py`

合意したツリーを JSON マニフェストに落とし、`python3 <skill-dir>/scripts/scaffold.py manifest.json [--root <dir>] [--dry-run] [--gitkeep]` で作成する。既存ファイルは上書きしない（スキップして報告する）。`.gitkeep` は既定では置かない（後から `Write` で埋めるディレクトリに残骸が残るため）。全ファイルを書き終えた後に `find . -type d -empty -not -path './.git/*' -exec touch {}/.gitkeep \;` で一括して置く。

```json
{
  "dirs": ["src", "tests", "docs", "docs/adr", ".claude/skills", ".claude/agents", ".claude/rules"],
  "files": {
    "README.md": "# project-name\n",
    ".claude/settings.json": "{\n  \"permissions\": { \"allow\": [], \"deny\": [] }\n}\n"
  }
}
```

大きな内容（CLAUDE.md、要件定義書）はマニフェストに埋め込まず、`Write` ツールで個別に書く方が読みやすい。マニフェストは骨格作りに使う。

---

## 2. 要件定義書 `docs/requirements.md`

④で確定した内容を書く。**「検討したが採用しなかった選択肢」と「未決事項」は必須節**。前者は同じ議論の再発を防ぎ、後者は「決めたつもり」の齟齬を防ぐ。

```markdown
# <プロジェクト名> 要件定義書

- 版: 0.1（初版）
- 日付: YYYY-MM-DD
- 作成: project-init による対話とレビューから作成

## 1. 背景と目的
（課題、なぜ今やるか。3〜6 行）

## 2. 対象ユーザー
（誰が、どんな状況で使うか。複数いれば優先順位）

## 3. スコープ
### 3.1 やること（初回リリース）
1. ...
### 3.2 やらないこと
- ...（理由を一言）
### 3.3 将来検討
- ...

## 4. 成功基準
（第三者が判定できる形。数値または具体的シナリオ）

## 5. 機能要件
（ユーザーストーリー or 機能一覧。優先度 Must / Should / Could）

## 6. 非機能要件
（性能・セキュリティ・可用性・運用・データ・対応環境・法規のうち関係するもの。無関係なものは「対象外」と明記）

## 7. 制約
（期限、技術、チーム、予算、既存システム）

## 8. リスクと対策
| リスク | 影響 | 対策 / 検知方法 |
|---|---|---|

## 9. 検討したが採用しなかった選択肢
| 選択肢 | 却下理由 | 再検討の条件 |
|---|---|---|

## 10. 未決事項
| 事項 | 決定期限 / トリガー | 暫定の進め方 |
|---|---|---|

## 11. 用語集
| 用語 | この文書での意味 |
|---|---|
```

設計判断の記録（ADR）が必要になったら `docs/adr/NNNN-<title>.md` に分ける。要件定義書には ADR への参照だけ置く。

---

## 3. `CLAUDE.md` と `.claude/rules/`

### 配置
- `./CLAUDE.md`（推奨。`./.claude/CLAUDE.md` でも同じ扱い。どちらか一方にする）
- `~/.claude/CLAUDE.md` は個人設定。プロジェクト用に触らない
- `./CLAUDE.local.md` は個人のプロジェクト固有メモ。`.gitignore` に入れる
- `@path/to/file` で他ファイルを取り込める（要確認: 現行ドキュメントで挙動を確認して使う）

### 方針
- **100〜200 行。** それ以上は `.claude/rules/` に分割
- 書くのは「Claude が知り得ないこと・誤りやすいこと」だけ。一般的な言語仕様、公式ドキュメントの内容、リンターが強制する規約は書かない
- 禁止事項には理由を添える（理由がないと例外判断ができない）
- 抽象的な精神論（「保守性の高いコードを」）は書かない。具体的な判断基準に落とすか削る
- **一時的な対処には賞味期限を付ける。** 今のモデルの弱点に合わせた回避策、ツールの不具合の迂回などは、その行に `<!-- 賞味期限: YYYY-MM -->` を付け、期限が来たら消すか更新する。恒久ルールと混ぜない。特定のツールや手順に執着させる指示も同じ扱い

### テンプレート

```markdown
# <プロジェクト名>

<一文で何を作っているか。要件定義書は docs/requirements.md>

## コマンド
- 開発サーバー: `...`
- テスト: `...`（単体のみ: `...`）
- リント / フォーマット: `...`
- ビルド: `...`
- 実行前に確認を取るもの: `<deploy 等>` — 理由: <本番に影響する等>

## 完了の定義（検証）
- 変更が「動いた」と言えるのは: `<テストコマンド>` と `<型チェック / リント>` が通ったとき
- UI の変更は開発サーバーを起動して実際に操作し、結果（スクリーンショット等）を報告する
- PR 前に必ず: `<チェックコマンド>`（`/pre-pr-check` skill があればそれ）
- レビュー: <誰が／何が見直すか（人 / CI / reviewer agent）>
- フィードバック: <どこから拾うか（Issue / Slack / ログ）、巡回の頻度>
- 大きなファイルは 200 行ずつ分割して読む <!-- 賞味期限: YYYY-MM。モデル更新時に見直す -->

## 構成
（ツリーではなく「どこに何を置くか」の原則を 3〜6 行。ツリーは README か docs へ）
- `src/features/<name>/` に機能単位で置く。層で分けない — 理由: ...
- `src/shared/` は 2 箇所以上から使われるものだけ

## アーキテクチャの境界
- `domain/` はフレームワークに依存しない。`infra/` からのみ import される
- DB アクセスは `repositories/` 経由。直接クエリを書かない — 理由: ...

## 規約（リンターで検出できないもの）
- エラーは握りつぶさず、`AppError` に包んで上位へ — 理由: ...
- ログは構造化（key=value）。個人情報を出さない

## ドメイン用語
- **ユーザー**: サービスにログインする人。管理者は含まない
- **ワークスペース**: ...

## Git
- ブランチ: `feat/<issue>-<slug>`, `fix/...`
- コミット: Conventional Commits。push は確認を取る

## Claude への期待
- 応答は日本語。要点を先に、理由は短く
- 不明点は推測で進めず質問する。ただし命名などの些事は自分で決めてよい
- 破壊的操作（削除、force push、本番 DB 変更）は必ず確認

## 参照
- 要件: `docs/requirements.md`
- 設計判断: `docs/adr/`
- パス限定ルール: `.claude/rules/`
```

### `.claude/rules/<topic>.md`
特定パスにだけ効くルール。`paths` frontmatter で対象を絞る。`paths` を省くとセッション開始時に常に読み込まれる（CLAUDE.md と同等）。サブディレクトリ可（`.claude/rules/frontend/react.md`）。

```markdown
---
paths:
  - "src/db/migrations/**"
---
# マイグレーション

- ファイル名は `YYYYMMDDHHMMSS_<verb>_<table>.sql`
- DOWN を必ず書く — 理由: ロールバック手順を運用が要求
- 本番適用は `scripts/migrate.sh --env prod` のみ。直接 psql しない
```

---

## 4. スキル `.claude/skills/<name>/SKILL.md`

### 作る基準
- この要件で **繰り返し発生する** 定型作業（リリース手順、マイグレーション作成、特定形式のドキュメント生成、テストデータ投入）
- 手順が 3 ステップ以上あり、毎回説明するのが無駄なもの
- ③で 3 ループが決まったなら、次の 2 つが候補の筆頭：
  - **PR 前チェック**（例 `pre-pr-check`）: テスト・リント・型チェック・差分の自己レビューを一つの手順に固め、結果を定型で報告する
  - **フィードバック巡回**（例 `feedback-sweep`）: Issue／Slack／ログから未対応のものを集めて要約し、対応候補を提案する
- 1〜3 個が目安。「コードを書く」「バグを直す」のような汎用作業はスキルにしない

### frontmatter（すべて任意。ディレクトリ名がデフォルトの name）

| フィールド | 意味 |
|---|---|
| `name` | スキル名の上書き。省略時はディレクトリ名 |
| `description` | **最重要。** 何をするか＋いつ使うかを具体的に。Claude はこれを見て自動発動を判断する |
| `disable-model-invocation` | `true` でユーザーの `/name` 呼び出し限定（自動発動しない）。副作用が大きい手順（デプロイ等）に付ける |
| `user-invocable` | `false` で `/` メニューから隠す（Claude の自動発動のみ） |
| `argument-hint` | `/name` 入力時のヒント。例 `"<migration-name>"` |
| `allowed-tools` | 使えるツールの CSV。例 `Read, Grep, Bash` |
| `model` | このスキル実行時のモデル |

本文中で `$ARGUMENTS`（引数全体）、`$0` `$1`（位置引数）が使える。`` !`command` `` で shell の標準出力を埋め込める。

**YAML の注意:** `description` に `: `（コロン＋空白）や `#` が含まれると unquoted では YAML エラーになる。description は常に二重引用符で囲む（agents、rules も同じ）。

旧来の `.claude/commands/<name>.md` も同じように動くが、補助ファイル（`references/`、`scripts/`）を同梱できるスキル形式を使う。

### テンプレート

```markdown
---
name: release
description: "バージョンを上げ、CHANGELOG を更新し、タグを打ってリリース PR を作る。ユーザーが「リリース」「バージョンアップ」「タグを打つ」と言ったとき、または /release で使う。"
disable-model-invocation: true
argument-hint: "<patch|minor|major>"
allowed-tools: Read, Edit, Bash, Grep
---

# リリース手順

引数 `$0` は `patch` / `minor` / `major`。省略時は `patch`。

1. `git status` がクリーンであることを確認する。差分があれば止めて報告する。
2. ...
3. ...

## 失敗したとき
- テストが落ちたらタグを打たない。原因を報告して終了する。
```

---

## 5. サブエージェント `.claude/agents/<name>.md`

### 作る基準
- **文脈を分離したい**（大量のファイルを読むレビュー、ログ解析）
- **権限を絞りたい**（読み取り専用レビュアー、テスト実行専任）
- **並列化したい**（複数モジュールの同時調査）
- 作る根拠を `description` に書く。根拠が書けないなら作らない

### frontmatter

| フィールド | 必須 | 意味 |
|---|---|---|
| `name` | ○ | kebab-case の一意な ID |
| `description` | ○ | いつ委譲するか。メインの Claude はこれを見て委譲を判断する |
| `tools` | | 使えるツールの CSV（許可リスト）。例 `Read, Grep, Glob, Bash` |
| `disallowedTools` | | 禁止リスト |
| `model` | | `sonnet` / `opus` / `haiku` / `inherit` など |
| `permissionMode` | | `default` / `acceptEdits` / `plan` など |
| `maxTurns` | | ターン上限 |
| `skills` | | 事前ロードするスキル名の CSV |
| `mcpServers` | | 使わせる MCP サーバー名の CSV |
| `memory` | | `user` / `project` / `local` — 永続メモリ（要確認: 環境による） |
| `background` | | `true` で常駐 |

本文はそのエージェントのシステムプロンプト。会話履歴は引き継がれないので、必要な文脈は本文か委譲時のプロンプトで渡す。

### テンプレート

```markdown
---
name: code-reviewer
description: "変更差分のレビュー専任。セキュリティ・性能・境界違反（domain→infra の逆依存など）を指摘する。ファイルの変更はしない。PR 作成前、または「レビューして」と言われたときに委譲する。読み取り専用にする理由: レビューと修正を分けて、レビュアーが自分の指摘を勝手に直さないようにするため。"
tools: Read, Grep, Glob, Bash
model: inherit
---

あなたはこのリポジトリのコードレビュアー。`git diff` を読み、次の順で指摘する：

1. 重大（セキュリティ、データ破損、境界違反）
2. バグの可能性
3. 可読性・保守性

各指摘に「ファイル:行 → 問題 → 修正案」を付ける。修正はしない。問題がなければ「指摘なし」と根拠を一行で。

プロジェクト固有の境界ルールは `CLAUDE.md` の「アーキテクチャの境界」節を読むこと。
```

### ファンアウト → 反証レビュー（明示オプトインのみ）

**条件: ③でユーザーが「複数の観点で並列にレビューしてほしい」「指摘を反証してほしい」と明示的に求めた場合だけ作る。** 既定では作らず、こちらから提案もしない。理由: エージェントが増えるほど実行コストと保守が増え、単一の `code-reviewer` で足りるプロジェクトが大半だから。この条件を緩めない。

構成：
1. 変更差分に対し、観点別（セキュリティ／性能／境界違反／可読性など）の reviewer を **並列** に起動して指摘を出させる（ファンアウト）。
2. 出た指摘ごとに `review-verifier` を起動し、「本当に問題か」を **反証** させる（再現手順、コード上の根拠、既存テストでの確認）。
3. 反証を生き残った指摘だけを人に上げる。人は設計判断だけをする。

観点別 reviewer は上の `code-reviewer` テンプレートの本文を観点ごとに絞ったものでよい。反証側のテンプレート：

```markdown
---
name: review-verifier
description: "レビュー指摘の反証専任。他のレビュアーが出した指摘一件を受け取り、コードと再現で「本当に問題か」を検証して、確認済み／誤検知／判定不能に振り分ける。ファイルの変更はしない。ファンアウトレビューの後段でのみ使う。分ける理由: 指摘を出す側と検証する側を分けないと、指摘の数だけ増えて人の確認負荷が下がらないため。"
tools: Read, Grep, Glob, Bash
model: inherit
---

あなたはレビュー指摘の検証者。委譲時に渡された **指摘一件**（ファイル:行、問題、修正案）について、次を行う：

1. 該当コードと、それを呼ぶ側・呼ばれる側を読む。指摘が前提にしている挙動が実際のコードと一致するか確かめる。
2. 再現できるなら再現する（テストの実行、最小の入力での動作確認）。副作用のあるコマンドは実行しない。
3. 判定を一つ選ぶ：**確認済み**（再現または根拠あり）／**誤検知**（前提が誤り。理由を示す）／**判定不能**（何が分かれば決まるかを示す）。

出力は「判定 → 根拠（ファイル:行）→ 元の修正案への意見」の 3 行以内。修正はしない。指摘を追加しない。
```

---

## 6. プラグイン `.claude-plugin/`

### 作る基準
- **複数プロジェクトで再利用する見込みがある** ときだけ。単一プロジェクトなら `.claude/skills/` と `.claude/agents/` に直接置き、プラグインは作らない（その旨をユーザーに説明する）
- チーム配布したいときも候補

### レイアウト（`.claude-plugin/` の中に入るのは `plugin.json` だけ。他はプラグインルート直下）

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── skills/<name>/SKILL.md
├── agents/<name>.md
├── hooks/hooks.json         （任意）
├── .mcp.json                （任意）
└── README.md
```

### `plugin.json`

```json
{
  "name": "my-plugin",
  "description": "何をするプラグインか一文で",
  "version": "0.1.0",
  "author": { "name": "..." }
}
```

`name` は kebab-case 必須。`skills` / `agents` / `commands` / `hooks` / `mcpServers` をパスで明示することもできるが、標準レイアウトに従えば省略できる。

### ローカルで試す
```
claude --plugin-dir ./my-plugin
claude plugin validate ./my-plugin
```

### 配布（マーケットプレイス）
マーケットプレイス（`.claude-plugin/marketplace.json`）経由で配布する。プラグインと同じリポジトリに置き、`source: "./"` で自分自身を指せる（`claude plugin marketplace add <owner>/<repo>` → `claude plugin install <plugin>@<marketplace>` で導入できることを実機で確認済み。2026-09）。

```json
{
  "name": "<marketplace-name>",
  "owner": { "name": "<owner>" },
  "plugins": [
    { "name": "<plugin-name>", "source": "./", "description": "一文で", "version": "0.1.0" }
  ]
}
```

- `plugins[].source` は `./` で始まる相対パス（マーケットプレイスのルート基準）か、`{"source": "github", "repo": "owner/repo"}` のようなオブジェクト
- `plugins[].version` は `plugin.json` の `version` と一致させる（`claude plugin tag` が不一致を検出する）
- 検証: `claude plugin validate --strict .claude-plugin/marketplace.json`
- 利用側のリポジトリで自動有効化するなら `.claude/settings.json` に `extraKnownMarketplaces`（`{"<name>": {"source": {"source": "github", "repo": "owner/repo"}}}`）と `enabledPlugins`（`{"<plugin>@<marketplace>": true}`）を書く

単一スキルだけのプラグインなら、ルートに `SKILL.md` を置き `plugin.json` に `"skills": ["./"]` と書く形も使える（`claude plugin init <name>` が生成する形。`~/.claude/skills/<name>/` に置くと `<name>@skills-dir` として自動で読み込まれる）。

---

## 7. MCP `.mcp.json`

### 進め方
1. 要件から外部接続を洗い出す（DB、GitHub/GitLab、ブラウザ操作、Figma、Slack、Notion、社内 API、ファイルストレージ）。③のフィードバックループで「声を拾う場所」に挙がったもの（Slack、Issue トラッカー）も候補に含める。
2. 候補ごとに **「何に使うか／なくても困らないか」** を添えてユーザーに提示し、採用を選ばせる。
3. 採用したものだけ書く。**実在を確認できないサーバー名・パッケージ名は書かない。** 不確かなら `claude mcp add` での追加手順と公式レジストリの案内にとどめる。
4. 秘密情報は `${VAR}` 参照。`.env.example` に変数名を列挙する。

### 形式

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": { "Authorization": "Bearer ${GITHUB_TOKEN}" }
    },
    "local-db": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "<package-name>", "${DATABASE_URL}"],
      "env": {}
    }
  }
}
```

- `type`: `stdio` / `http` / `sse`
- stdio: `command`, `args`, `env`
- http/sse: `url`, `headers`
- `${VAR}` と `${VAR:-default}` が `command` / `args` / `env` / `url` / `headers` で展開される
- `${CLAUDE_PROJECT_DIR}` でプロジェクトルートを参照できる

上の `url` / パッケージ名は **例**。生成時は必ずそのサーバーの公式ドキュメントの値に置き換えるか、ユーザーに確認する。

### 有効化
プロジェクトの `.mcp.json` は初回にユーザー承認を求められる。チームで自動承認したい場合は `.claude/settings.json` の `enableAllProjectMcpServers: true` または `enabledMcpjsonServers: ["name"]`（要確認）。

---

## 8. `.claude/settings.json` と hooks

### 権限

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run test:*)",
      "Bash(npm run lint)",
      "Bash(git status)",
      "Bash(git diff:*)"
    ],
    "ask": [
      "Bash(git push:*)"
    ],
    "deny": [
      "Bash(rm -rf:*)",
      "Bash(git push --force:*)",
      "Read(./.env)",
      "Read(./.env.local)",
      "Read(./.env.production)"
    ]
  }
}
```

- `allow` は「聞かずに実行」、`ask` は「毎回確認」、`deny` は「禁止」。deny が最優先
- `.env` の deny はファイル名を個別に列挙する。`Read(./.env.*)` と書くと `.env.example` まで読めなくなり、Claude が必要な変数名を確認できない
- ③で聞いた「確認なしに実行してほしくないコマンド」を `ask`、「実行してはいけない」を `deny` に落とす
- `.claude/settings.local.json` は個人用。`.gitignore` へ

### hooks（必要なときだけ）

典型：編集後に自動フォーマット。

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          { "type": "command", "command": "npx prettier --write \"$CLAUDE_FILE_PATH\" 2>/dev/null || true" }
        ]
      }
    ]
  }
}
```

主なイベント: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PermissionRequest`, `Notification`, `Stop`, `SubagentStop`。hook は stdin で JSON を受け取る。環境変数名や JSON スキーマの詳細は公式 hooks ドキュメントで確認する（上の `$CLAUDE_FILE_PATH` は要確認 — 確実なのは stdin JSON の `tool_input.file_path` を読む方法）。

hooks は挙動を暗黙に変えるので、生成したら CLAUDE.md の「コマンド」節に「編集後は自動フォーマットされる」と一言書く。

---

## 9. `.gitignore` / `.env.example`

`.gitignore` に追加（既存なら追記）：
```
.env
.env.*
!.env.example
.claude/settings.local.json
CLAUDE.local.md
```

`.env.example`：`.mcp.json` と settings で参照した `${VAR}` を全部列挙。値は空か説明。
```
# GitHub MCP 用。repo スコープの PAT
GITHUB_TOKEN=
# ローカル DB
DATABASE_URL=postgres://user:pass@localhost:5432/app
```

---

## 10. 生成後のユーザー向け案内

最後に 3〜5 行で「次にやること」を示す。例：

1. `.env.example` を `.env` にコピーして値を入れる
2. `claude` を起動し、`.mcp.json` のサーバー承認と `/project-init` で作ったスキルの動作確認
3. プラグインを作った場合は `claude plugin validate ./<plugin>`
4. `git add -A && git commit -m "chore: scaffold project with project-init"`
5. 要件定義書の「未決事項」の期限を確認する
6. CLAUDE.md の `<!-- 賞味期限 -->` 付きの行の見直し時期を控える（モデルやツールの更新時にも見直す）
