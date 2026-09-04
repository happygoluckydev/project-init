#!/bin/sh
# project-init スキルを ~/.claude/skills/project-init に入れる（初回は clone、2 回目以降は pull）。
# マーケットプレイス経由（README 参照）が使えない環境向けの代替手段。
#
#   sh install.sh                 # 既定: https://github.com/happygoluckydev/project-init
#   REPO=<git url> sh install.sh  # fork などを使う場合
#   DEST=<dir>     sh install.sh  # 置き場所を変える場合（既定: ~/.claude/skills/project-init）
set -eu

REPO="${REPO:-https://github.com/happygoluckydev/project-init}"
DEST="${DEST:-$HOME/.claude/skills/project-init}"

if [ -d "$DEST/.git" ]; then
  echo "更新: $DEST"
  git -C "$DEST" pull --ff-only
elif [ -e "$DEST" ]; then
  echo "エラー: $DEST は既に存在しますが git リポジトリではありません。手で確認してください。" >&2
  exit 1
else
  echo "取得: $REPO -> $DEST"
  mkdir -p "$(dirname "$DEST")"
  git clone --depth 1 "$REPO" "$DEST"
fi

echo
echo "完了。次のセッションから /project-init が使えます（起動中のセッションでは /reload-plugins）。"
echo "確認: claude plugin list   （project-init@skills-dir が loaded なら OK）"
