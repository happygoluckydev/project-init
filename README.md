# project-init

Claude Code 用スキル **`/project-init`** の配布リポジトリ。

プロジェクト立ち上げ時に、要件・フォルダ構成・CLAUDE.md の内容を段階的にインタビューし、その回答をクリティカル／ラテラルの両輪でレビューしてから、フォルダ構成・要件定義書・CLAUDE.md・プロジェクト用スキル・サブエージェント・プラグイン雛形・`.mcp.json` を一括生成する。詳細は [SKILL.md](SKILL.md)。

このリポジトリは **それ自体が 1 つのスキルであり、同時に 1 つのプラグイン、1 つのマーケットプレイス** になっている。どの環境でも、下のいずれかの方法でそのまま使える。

```
project-init/
├── SKILL.md                    スキル本体（Claude が読む手順）
├── references/                 質問リスト、レビュー観点、生成ガイド
├── scripts/scaffold.py         フォルダ雛形を作る補助スクリプト
├── assets/                     scaffold.py 用のマニフェスト例
├── .claude-plugin/
│   ├── plugin.json             プラグイン定義（skills: ["./"] でルートをスキルとして読む）
│   └── marketplace.json        このリポジトリ自身を配るマーケットプレイス定義
├── .claude/                    このリポジトリで作業する Claude 向け（CLAUDE.md、settings、hooks、専用スキル。配布物には含めない）
├── docs/                       要件定義書と update-watch のベースライン（配布物には含めない）
├── tools/package.py            配布用アーカイブ（.skill / plugin zip）を作る
└── .github/workflows/          CI（検証）とリリース（アーカイブ添付）
```

## インストール

普段使う経路は A。B〜E は環境の都合で A が使えないときのため。

### A. Claude Code（CLI・デスクトップアプリ・IDE 拡張）— 普段はこれ

マーケットプレイスとして登録してインストールする。更新も `update` で追従できる。

```bash
claude plugin marketplace add happygoluckydev/project-init
claude plugin install project-init@happygoluckydev
```

Claude Code の中なら `/plugin marketplace add happygoluckydev/project-init` → `/plugin install project-init@happygoluckydev`。

更新:

```bash
claude plugin marketplace update happygoluckydev
claude plugin update project-init@happygoluckydev
```

### その他の経路

#### B. `~/.claude/skills/` に clone（マーケットプレイスが使えない環境）

リポジトリのルートに `SKILL.md` と `.claude-plugin/plugin.json` があるので、clone するだけで `project-init@skills-dir` として自動で読み込まれる。

```bash
git clone https://github.com/happygoluckydev/project-init ~/.claude/skills/project-init
# 更新は git pull
```

Windows は `%USERPROFILE%\.claude\skills\project-init` に clone する。

> **A と B は併用しない。** 両方入れると名前が衝突し、マーケットプレイス版が優先されて `skills-dir` 側は読み込まれない（`claude plugin list` に警告が出る）。

#### C. リポジトリ単位で有効化（チーム共有・Claude Code on the web）

対象プロジェクトの `.claude/settings.json` に次を書いてコミットすると、そのリポジトリを開いた全員（web セッションを含む）で自動的に有効になる。個人環境へのインストールは不要。

```json
{
  "extraKnownMarketplaces": {
    "happygoluckydev": {
      "source": { "source": "github", "repo": "happygoluckydev/project-init" }
    }
  },
  "enabledPlugins": {
    "project-init@happygoluckydev": true
  }
}
```

#### D. そのセッションだけ試す

```bash
# ローカルの clone から
claude --plugin-dir /path/to/project-init

# Releases の zip を直接
claude --plugin-url https://github.com/happygoluckydev/project-init/releases/latest/download/project-init-plugin.zip
```

#### E. claude.ai / Claude デスクトップアプリ（チャット）

[Releases](https://github.com/happygoluckydev/project-init/releases) の `project-init.skill` をダウンロードし、claude.ai の設定（Settings → Capabilities / Skills）からアップロードする。claude.ai にアップロードしたスキルは、同じアカウントの Claude Code on the web セッションにも同期スキルとして読み込まれる（ただしこの同期はアップロード時点の内容で止まるので、リポジトリを更新したら `.skill` を作り直して再アップロードする）。

手元で作るなら:

```bash
python3 tools/package.py     # dist/project-init.skill と dist/project-init-plugin.zip
```

## 使い方

```
/project-init 家計簿アプリ
```

引数はプロジェクト名や一言説明。省略しても動く。以降は 5 フェーズ（要件 → フォルダ構成 → CLAUDE.md → レビュー → 生成）を対話で進める。詳細は [SKILL.md](SKILL.md)。

## 開発

- スキル本体は `SKILL.md` と `references/`。`scripts/` と `assets/` はスキルの一部として配布される。`tools/` と `.github/` は配布に含まれない。
- 変更を試す: `claude --plugin-dir .` で起動して `/project-init` を打つ。
- PR 前: `/pre-pr-check`（検証コマンド 3 本、手動確認シナリオ、PR 本文用の自己レビュー文）。
- Claude Code の更新への追随: `/update-watch`（CHANGELOG・docs・モデル一覧を `docs/update-watch/` のベースラインと比べ、影響箇所と修正案を Issue にする）。セッション開始時の hook が版の差を知らせ、週次の Routine でも実行する。取り込んだら `python3 .claude/skills/update-watch/scripts/fetch.py --baseline` でベースラインを更新する。

- リリース:
  1. `.claude-plugin/plugin.json` と `.claude-plugin/marketplace.json` の `version` を同じ値に上げてコミットする。
  2. `claude plugin tag --push` で `project-init--v<version>` タグを作って push する（両ファイルの version が一致していることも検証される）。タグ形式はこれだけ。
  3. `Release` ワークフローが `project-init.skill` と `project-init-plugin.zip` を添付した GitHub Release を作る。
  4. 利用者は `claude plugin marketplace update happygoluckydev && claude plugin update project-init@happygoluckydev` で追従する。
