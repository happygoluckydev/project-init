#!/usr/bin/env python3
"""update-watch の取得と差分（標準ライブラリ＋curl）。

Usage:
    python3 fetch.py [--work DIR]     取得して差分を作る（既定の DIR: /tmp/update-watch）
    python3 fetch.py --baseline       取得した最新をベースラインにする（人が取り込み後に実行）

出力（--work 配下）:
    CHANGELOG.md            取得した全文
    changelog-new.md        ベースライン版より新しい節だけ
    changelog-relevant.md   新しい節のうち、スキルに関係するキーワードを含む行だけ
    docs/<name>.md          取得した各ページ
    diff/<name>.diff        docs/update-watch/snapshots/<name>.md との unified diff（差分がある場合のみ）
    summary.json            版・件数・失敗した取得

ベースラインは docs/update-watch/baseline.md の「- Claude Code: X.Y.Z」と「- 最終確認日: YYYY-MM-DD」。
--baseline は snapshots/ を取得結果で置き換え、この 2 行を書き換える。
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
BASELINE_MD = REPO / "docs" / "update-watch" / "baseline.md"
SNAPSHOTS = REPO / "docs" / "update-watch" / "snapshots"

CHANGELOG_URL = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
DOCS = {
    "skills": "https://code.claude.com/docs/en/skills.md",
    "plugins": "https://code.claude.com/docs/en/plugins.md",
    "plugin-marketplaces": "https://code.claude.com/docs/en/plugin-marketplaces.md",
    "settings": "https://code.claude.com/docs/en/settings.md",
    "hooks": "https://code.claude.com/docs/en/hooks.md",
    "sub-agents": "https://code.claude.com/docs/en/sub-agents.md",
    "memory": "https://code.claude.com/docs/en/memory.md",
    "mcp": "https://code.claude.com/docs/en/mcp.md",
    "claude-directory": "https://code.claude.com/docs/en/claude-directory.md",
    "models": "https://platform.claude.com/docs/en/models/overview.md",
}
# CHANGELOG の行をこのスキルに関係あるものに絞るキーワード（小文字比較）
KEYWORDS = [
    "skill", "plugin", "marketplace", "frontmatter", "claude.md", "rules", "memory",
    "setting", "permission", "hook", "agent", "mcp", "slash command", "/plugin",
    "--plugin-dir", "$arguments", "argument-hint", "disable-model-invocation",
    "model", "fable", "opus", "sonnet", "haiku",
]


def read_baseline() -> tuple[str, str]:
    text = BASELINE_MD.read_text(encoding="utf-8")
    v = re.search(r"^- Claude Code: (\d+\.\d+\.\d+)", text, re.M)
    d = re.search(r"^- 最終確認日: (\d{4}-\d{2}-\d{2})", text, re.M)
    if not v or not d:
        sys.exit(f"{BASELINE_MD}: 「- Claude Code: X.Y.Z」「- 最終確認日: YYYY-MM-DD」の行が要ります")
    return v.group(1), d.group(1)


def write_baseline(version: str, date: str) -> None:
    text = BASELINE_MD.read_text(encoding="utf-8")
    text = re.sub(r"^- Claude Code: \d+\.\d+\.\d+", f"- Claude Code: {version}", text, flags=re.M)
    text = re.sub(r"^- 最終確認日: \d{4}-\d{2}-\d{2}", f"- 最終確認日: {date}", text, flags=re.M)
    BASELINE_MD.write_text(text, encoding="utf-8")


def vtuple(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split("."))


def fetch(url: str, dest: Path) -> str | None:
    """curl で取得する。成功なら None、失敗なら理由を返す。"""
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(
        ["curl", "-sSL", "-m", "60", "-o", str(dest), "-w", "%{http_code}", url],
        capture_output=True, text=True,
    )
    code = r.stdout.strip()
    if r.returncode != 0:
        return f"curl failed: {r.stderr.strip()[:200]}"
    if code != "200":
        return f"HTTP {code}"
    return None


def split_changelog(text: str) -> list[tuple[str, str]]:
    """[(version, body)] を新しい順で返す。"""
    out: list[tuple[str, str]] = []
    cur: str | None = None
    buf: list[str] = []
    for line in text.splitlines():
        m = re.match(r"^## (\d+\.\d+\.\d+)", line)
        if m:
            if cur:
                out.append((cur, "\n".join(buf)))
            cur, buf = m.group(1), [line]
        elif cur:
            buf.append(line)
    if cur:
        out.append((cur, "\n".join(buf)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", default="/tmp/update-watch")
    ap.add_argument("--baseline", action="store_true", help="取得結果をベースラインにする")
    args = ap.parse_args()

    work = Path(args.work)
    (work / "docs").mkdir(parents=True, exist_ok=True)
    (work / "diff").mkdir(parents=True, exist_ok=True)
    base_version, base_date = read_baseline()
    summary: dict = {"baseline": {"claude_code": base_version, "date": base_date}, "errors": {}}

    # 1. CHANGELOG
    err = fetch(CHANGELOG_URL, work / "CHANGELOG.md")
    latest = None
    if err:
        summary["errors"]["changelog"] = err
    else:
        sections = split_changelog((work / "CHANGELOG.md").read_text(encoding="utf-8"))
        latest = sections[0][0] if sections else None
        new = [(v, b) for v, b in sections if vtuple(v) > vtuple(base_version)]
        (work / "changelog-new.md").write_text("\n\n".join(b for _, b in new) + "\n", encoding="utf-8")
        relevant: list[str] = []
        for v, b in new:
            hits = [l for l in b.splitlines() if l.startswith("-") and any(k in l.lower() for k in KEYWORDS)]
            if hits:
                relevant.append(f"## {v}\n" + "\n".join(hits))
        (work / "changelog-relevant.md").write_text("\n\n".join(relevant) + "\n", encoding="utf-8")
        summary["changelog"] = {
            "latest": latest,
            "new_versions": [v for v, _ in new],
            "relevant_lines": sum(len(r.splitlines()) - 1 for r in relevant),
        }

    # 2. docs とスナップショットの差分
    changed: list[str] = []
    for name, url in DOCS.items():
        dest = work / "docs" / f"{name}.md"
        err = fetch(url, dest)
        if err:
            summary["errors"][name] = err
            continue
        snap = SNAPSHOTS / f"{name}.md"
        if not snap.exists():
            changed.append(name)
            (work / "diff" / f"{name}.diff").write_text(f"(no snapshot for {name})\n", encoding="utf-8")
            continue
        a = snap.read_text(encoding="utf-8").splitlines(keepends=True)
        b = dest.read_text(encoding="utf-8").splitlines(keepends=True)
        diff = list(difflib.unified_diff(a, b, f"snapshots/{name}.md", f"latest/{name}.md", n=2))
        if diff:
            changed.append(name)
            (work / "diff" / f"{name}.diff").write_text("".join(diff), encoding="utf-8")
    summary["docs_changed"] = changed

    (work / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    # 3. ベースライン更新（人が実行）
    if args.baseline:
        if summary["errors"]:
            print("取得に失敗したものがあるのでベースラインは更新しません:", summary["errors"], file=sys.stderr)
            return 1
        SNAPSHOTS.mkdir(parents=True, exist_ok=True)
        for name in DOCS:
            shutil.copyfile(work / "docs" / f"{name}.md", SNAPSHOTS / f"{name}.md")
        write_baseline(latest or base_version, dt.date.today().isoformat())
        print(f"\nベースライン更新: Claude Code {latest or base_version}, {dt.date.today().isoformat()}, snapshots {len(DOCS)} 件")
        print("差分を確認してコミットしてください（git diff docs/update-watch）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
