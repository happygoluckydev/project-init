#!/bin/sh
# SessionStart hook: Claude Code の版が docs/update-watch/baseline.md より新しければ /update-watch を促す。
# 何かあっても静かに終わる（exit 0）。ネットワークは使わない。
set -u
ROOT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
BASE="$ROOT/docs/update-watch/baseline.md"
[ -f "$BASE" ] || exit 0
command -v claude >/dev/null 2>&1 || exit 0

current="$(claude --version 2>/dev/null | sed -n 's/^\([0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\).*/\1/p' | head -1)"
baseline="$(sed -n 's/^- Claude Code: \([0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\).*/\1/p' "$BASE" | head -1)"
checked="$(sed -n 's/^- 最終確認日: \([0-9-]*\).*/\1/p' "$BASE" | head -1)"
[ -n "$current" ] && [ -n "$baseline" ] || exit 0

newest="$(printf '%s\n%s\n' "$baseline" "$current" | sort -V | tail -1)"
if [ "$newest" = "$current" ] && [ "$current" != "$baseline" ]; then
  echo "update-watch: Claude Code が $baseline → $current に上がっています（最終確認 $checked）。このセッションの最初の応答で、ユーザーに /update-watch の実行を一行で提案してください。自動では実行しないこと。"
fi
exit 0
