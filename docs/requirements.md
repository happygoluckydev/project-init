# project-init リポジトリ 要件定義書（構成見直し）

- 版: 0.1（初版）
- 日付: 2026-09-04
- 作成: `/project-init` による対話とレビューから作成

## 1. 背景と目的

このリポジトリは Claude Code 用スキル `/project-init` そのもので、ルートがスキル・プラグイン・マーケットプレイスの 3 役を兼ねる。配布経路は整ったが、**Claude／Claude Code の更新に追随する仕組みがない**。SKILL.md と `references/` は Claude Code の仕様（frontmatter、settings のキー、plugin 形式）に依存しており、仕様が変わると生成物が古くなる。更新を検知し、影響箇所と修正案を出す仕組みを作り、あわせて構成・検証手順・CLAUDE.md を整える。

## 2. 対象ユーザー

自分だけ（happygoluckydev）。複数の環境（Claude Code CLI、デスクトップ、web セッション、claude.ai）で同じスキルを使う。チーム配布・公開は想定しない。

## 3. スコープ

### 3.1 やること（今回）
1. 更新監視スキル `/update-watch`（リポジトリ専用）: CHANGELOG・公式 docs・モデル一覧を取得し、ベースラインとの差分から影響箇所と修正案を Issue にまとめる
2. 起動時の版比較 hook: このリポジトリのセッション開始時に `claude --version` とベースラインを比べ、上がっていれば `/update-watch` の実行を促す
3. 週次の Routine: 新規セッションで `/update-watch` を実行する
4. `/pre-pr-check` スキル: 検証コマンド、手動確認シナリオ、PR 本文用の自己レビュー文
5. `.claude/CLAUDE.md` に検証・レビュー・フィードバックの 3 ループと push 確認を明記。`.claude/settings.json` で `git push` を ask、force push を deny
6. 配布経路の整理（`install.sh` 削除、リリースタグを 1 形式に、README の並べ替え）
7. CI に `scripts/scaffold.py` のスモークテスト
8. `references/scaffold-guide.md` §6 を検証済みの marketplace 形式に更新。「要確認」項目を監視のチェックリスト化

### 3.2 やらないこと
- 修正案の自動マージ — 取り込みは必ず人が判断する
- 英語ドキュメント・LICENSE — 自分専用のため
- スキルの自動評価（evals）を CI で回す — 動作確認は手動のまま。手順だけ固定する
- claude.ai 側の `.skill` 再アップロードの自動化 — 手動

### 3.3 将来検討
- 監視のノイズ量に応じたフィルタ強化（キーワードの追加・除外）
- evals の整備（`/project-init` の会話を数シナリオで採点）

## 4. 成功基準

- Claude Code の新版が出た後、次の `/update-watch` 実行で **影響する SKILL.md／references の箇所（ファイル:行）と修正案が Issue 1 件にまとまる**。影響がなければ Issue を立てず、実行結果だけ残る
- このリポジトリでセッションを開いたとき、Claude Code の版がベースラインより新しければ、最初の応答で `/update-watch` の実行が提案される
- 変更後に `/pre-pr-check` の検証コマンド 3 本が通り、確認シナリオ 3 本がチェックリストとして提示される

## 5. 機能要件

| 優先 | 要件 |
|---|---|
| Must | `/update-watch` が CHANGELOG のベースライン版より新しい節を抽出し、スキルに関係するキーワードで絞る |
| Must | `/update-watch` が docs 9 ページとモデル一覧をスナップショットと比較し、差分を出す |
| Must | `/update-watch` が影響箇所を `SKILL.md` / `references/*.md` の行番号付きで示し、Issue 本文を作る。同じ版の Issue があれば作らない |
| Must | ベースライン（版・日付・スナップショット）は人が `fetch.py --baseline` で更新する。自動実行は読み取りと Issue 作成のみ |
| Must | SessionStart hook は数百ミリ秒以内に終わり、失敗しても静かに終了する |
| Should | `/update-watch` が「要確認リスト」（`docs/update-watch/baseline.md`）の各項目を最新 docs で点検する |
| Should | `/pre-pr-check` が PR 本文用の自己レビュー文（影響フェーズ、参照 §番号、賞味期限行）を生成する |

## 6. 非機能要件

- **ネットワーク**: この環境から GitHub API は使えない（403）。取得は `raw.githubusercontent.com`、`code.claude.com/docs`、`platform.claude.com/docs` に限る。取得失敗は報告して続行する
- **コスト**: hook はトークンを使わない。Routine は週 1 回、1 セッション分
- 性能・セキュリティ・可用性・i18n・法規: 対象外

## 7. 制約

- 利用者が自分だけなので、push と Issue／PR 作成は人が判断する（push は確認を取る）
- Python は標準ライブラリのみ。取得は `curl`（プロキシと CA 設定を引き継ぐため）

## 8. リスクと対策

| リスク | 影響 | 対策 / 検知方法 |
|---|---|---|
| 監視のノイズが多く Issue が読まれなくなる | 仕組みが形骸化する | まず手動で回してノイズを見る。キーワードで絞り、影響なしなら Issue を立てない |
| docs の URL 変更で取得が失敗する | 差分が取れない | `llms.txt` の目次で URL を確認する手順をスキルに書く。失敗はそのまま報告 |
| Routine のセッションに GitHub ツールがない | Issue が作れない | 本文を出力して終わる。次回の手動実行で作る |
| スナップショット（数百 KB）がプラグインのキャッシュにも入る | インストール容量が増える | 実害は小さい。増えすぎたら配布用に別ディレクトリへ分ける |

## 9. 検討したが採用しなかった選択肢

| 選択肢 | 却下理由 | 再検討の条件 |
|---|---|---|
| GitHub Actions の cron で `claude -p` を回す | API キーと課金が要る。Routine なら購読内で動く | Routine が使えない環境に移ったとき |
| GitHub API（releases）で新版を検知 | この環境から 403 | ネットワークポリシーが変わったとき |
| 監視スキルを project-init の配布物に同梱 | 利用者が自分だけ。ルートに SKILL.md を置く今のレイアウトを崩す | 他人に配るとき |
| evals を CI で自動実行 | 費用と保守が先行する。まず手順の固定で足りる | 手動確認で見逃しが 2 回以上起きたとき |
| `install.sh` を残す | README の `git clone` 1 行と同じ | なし |
| 修正案を PR として自動作成 | 自動実行が push を伴う。push は確認する方針と矛盾 | 監視のノイズが十分低いと分かったとき |

## 10. 未決事項

| 事項 | 決定期限 / トリガー | 暫定の進め方 |
|---|---|---|
| 監視のノイズ判定基準（何件以上で絞るか） | 手動実行 2〜3 回後 | 初回はすべて列挙 |
| plugin の `version` を上げる時期 | scaffold-guide の更新を main に入れるとき | 1.1.0 を候補にする |
| claude.ai 側の同期スキルの更新 | リリースのたび | README の手順で手動アップロード |

## 11. 用語集

| 用語 | この文書での意味 |
|---|---|
| ベースライン | 最後に人が「確認済み」とした Claude Code の版・日付・docs のスナップショット |
| 要確認リスト | `references/scaffold-guide.md` で「要確認」と付けた仕様項目の一覧。監視のたびに点検する |
| 3 ループ | 検証（動いたと確かめる）・レビュー（変更を見直す）・フィードバック（使った人の声を拾う） |
