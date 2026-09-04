#!/usr/bin/env python3
"""project-init スキルを配布用アーカイブにまとめる（標準ライブラリのみ）。

Usage:
    python3 tools/package.py            # dist/ に 2 つのアーカイブを作る
    python3 tools/package.py --check    # 検証だけ行い、何も書き出さない
    python3 tools/package.py --out DIR  # 出力先を変える（既定: dist/）

出力:
    dist/project-init.skill        claude.ai / Claude デスクトップアプリに
                                   アップロードする形式。zip の中身は
                                   project-init/SKILL.md, references/, scripts/, assets/
    dist/project-init-plugin.zip   `claude --plugin-dir` / `--plugin-url` に渡す形式。
                                   上記に .claude-plugin/plugin.json を加えたもの

検証:
    - SKILL.md の frontmatter に name / description があり、name が "project-init"、
      name は 64 文字以内、description は 1024 文字以内（claude.ai の上限）
    - .claude-plugin/plugin.json と marketplace.json の version が一致している
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_NAME = "project-init"
# スキル本体として配布するもの。README や CI 設定は含めない。
PAYLOAD = ["SKILL.md", "references", "scripts", "assets"]
EXCLUDE_DIRS = {"__pycache__", "node_modules", ".git"}
EXCLUDE_FILES = {".DS_Store", "Thumbs.db"}
EXCLUDE_SUFFIXES = {".pyc"}


def parse_frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    if not m:
        raise SystemExit("SKILL.md: YAML frontmatter（--- で囲まれた先頭ブロック）がありません")
    try:  # PyYAML があれば正確に読む
        import yaml  # type: ignore

        data = yaml.safe_load(m.group(1))
        if not isinstance(data, dict):
            raise SystemExit("SKILL.md: frontmatter が辞書ではありません")
        return {k: str(v) for k, v in data.items()}
    except ImportError:
        pass
    data: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.startswith((" ", "\t")):
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        data[key.strip()] = value
    return data


def check() -> list[str]:
    problems: list[str] = []
    skill_md = ROOT / "SKILL.md"
    if not skill_md.exists():
        return ["SKILL.md がありません"]
    fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    name = fm.get("name", "")
    desc = fm.get("description", "")
    if name != SKILL_NAME:
        problems.append(f"SKILL.md: name は {SKILL_NAME!r} であるべきです（現在: {name!r}）")
    if len(name) > 64:
        problems.append(f"SKILL.md: name が 64 文字を超えています（{len(name)}）")
    if not desc:
        problems.append("SKILL.md: description が空です")
    elif len(desc) > 1024:
        problems.append(f"SKILL.md: description が 1024 文字を超えています（{len(desc)}）")

    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    entry = next((p for p in market.get("plugins", []) if p.get("name") == SKILL_NAME), None)
    if plugin.get("name") != SKILL_NAME:
        problems.append(f"plugin.json: name は {SKILL_NAME!r} であるべきです")
    if entry is None:
        problems.append(f"marketplace.json: plugins に {SKILL_NAME!r} がありません")
    elif entry.get("version") != plugin.get("version"):
        problems.append(
            "version が一致しません: plugin.json="
            f"{plugin.get('version')!r} marketplace.json={entry.get('version')!r}"
        )
    for rel in PAYLOAD:
        if not (ROOT / rel).exists():
            problems.append(f"{rel} がありません")
    return problems


def iter_payload():
    for rel in PAYLOAD:
        p = ROOT / rel
        if p.is_file():
            yield p
            continue
        for f in sorted(p.rglob("*")):
            if not f.is_file():
                continue
            parts = f.relative_to(ROOT).parts
            if any(d in EXCLUDE_DIRS for d in parts[:-1]):
                continue
            if f.name in EXCLUDE_FILES or f.suffix in EXCLUDE_SUFFIXES:
                continue
            yield f


def write_zip(path: Path, extra: list[Path]) -> int:
    count = 0
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in list(iter_payload()) + extra:
            arcname = Path(SKILL_NAME) / f.relative_to(ROOT)
            zf.write(f, arcname.as_posix())
            count += 1
    return count


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="検証のみ")
    ap.add_argument("--out", default="dist", help="出力先ディレクトリ（既定: dist）")
    args = ap.parse_args()

    problems = check()
    if problems:
        print("検証エラー:")
        for p in problems:
            print(f"  - {p}")
        return 1
    version = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    print(f"検証 OK: {SKILL_NAME} v{version}")
    if args.check:
        return 0

    out = Path(args.out)
    if not out.is_absolute():
        out = ROOT / out
    out.mkdir(parents=True, exist_ok=True)

    skill = out / f"{SKILL_NAME}.skill"
    n = write_zip(skill, [])
    print(f"書き出し: {skill.relative_to(ROOT)} ({n} files)")

    plugin_zip = out / f"{SKILL_NAME}-plugin.zip"
    n = write_zip(plugin_zip, [ROOT / ".claude-plugin" / "plugin.json"])
    print(f"書き出し: {plugin_zip.relative_to(ROOT)} ({n} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
