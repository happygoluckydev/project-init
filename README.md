# project-init

Claude Code 用スキル。要件・フォルダ構成・CLAUDE.md の中身を対話で聞き取り、クリティカル／ラテラルの両輪でレビューしてから、要件定義書・CLAUDE.md・skills・agents・MCP 設定などを一括生成する。手順の本体は [`SKILL.md`](SKILL.md)。

## 導入

いずれか一つ。

| 方法 | 手順 |
|---|---|
| 個人スキルとして置く | このリポジトリを `~/.claude/skills/project-init/` にクローン（またはコピー）する |
| プロジェクト専用にする | 対象リポジトリの `.claude/skills/project-init/` に置く |
| claude.ai のスキル同期 | claude.ai 側にアップロードすると `~/.claude/skills/synced/…/project-init/` に同期される。**このリポジトリを更新したら再アップロードしないと古いままになる** |

導入後、Claude Code で `/project-init <プロジェクト名や一言>` と打つ。既存プロジェクトの見直しにも使える（`/project-init このプロジェクトの構成を見直して`）。

## 構成

```
project-init/
├── SKILL.md                     # 手順本体（5 フェーズ）。毎回これだけが最初に読まれる
├── references/
│   ├── questions.md             # ①〜③の質問バンク（「なぜ聞くか」付き）
│   ├── review-lenses.md         # ④のレビューレンズとレポート形式
│   └── scaffold-guide.md        # ⑤の各成果物テンプレートと Claude Code の仕様
├── scripts/
│   ├── scaffold.py              # JSON マニフェストからツリーを作る（上書きしない）
│   └── validate.py              # 生成後の検証（frontmatter / JSON / CLAUDE.md 行数）
├── tests/test_scaffold.py       # 上 2 本のテスト
└── CLAUDE.md                    # このリポジトリを編集するときの注意
```

## 開発

```
python3 -m unittest discover -s tests        # scripts のテスト
python3 scripts/validate.py --no-tree        # SKILL.md 自身の frontmatter 検査
```

`SKILL.md` は 150 行以内、`references/` の各ファイルは必要になったときだけ読まれる前提で書く。仕様（frontmatter のフィールド名等）は公式ドキュメントで確認できたものだけを書き、未確認のものは「要確認」と付ける。

## 検討したが採用しなかった選択肢

| 選択肢 | 却下理由 | 再検討の条件 |
|---|---|---|
| `.claude-plugin/plugin.json` を付けてプラグイン化 | 単一スキルで、個人スキル配置か claude.ai 同期で足りる | チームや複数マシンへ配布したくなったとき |
| `assets/manifest.example.json` を残す | SKILL.md から参照されておらず、`scaffold-guide.md` §1 の例と重複していた | マニフェストの例が 2 つ以上必要になったとき |
