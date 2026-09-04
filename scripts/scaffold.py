#!/usr/bin/env python3
"""Create a directory/file skeleton from a JSON manifest without overwriting anything.

Usage:
    python3 scaffold.py manifest.json [--root DIR] [--dry-run] [--gitkeep]

Manifest format:
    {
      "dirs":  ["src", "tests", ".claude/skills"],
      "files": {"README.md": "# name\n", "docs/.gitkeep": ""}
    }

Behaviour:
    - Directories are created recursively (mkdir -p).
    - Files are written only if they do not exist; existing files are reported as SKIP.
    - With --gitkeep, directories listed in "dirs" that are still empty get a .gitkeep.
      Off by default: dirs you will fill later with other tools would otherwise keep a stray .gitkeep.
    - Paths that escape --root (e.g. "../x" or absolute paths) are rejected.
    - Prints a tree of everything under --root at the end (ignoring node_modules/.git/venvs).
"""
import argparse
import json
import os
import sys
from pathlib import Path

IGNORE = {"node_modules", ".git", ".venv", "venv", "__pycache__", "dist", "build", ".next"}


def safe_join(root: Path, rel: str) -> Path:
    p = (root / rel).resolve()
    if root.resolve() not in p.parents and p != root.resolve():
        raise ValueError(f"path escapes root: {rel}")
    return p


def tree(root: Path, prefix: str = "") -> list[str]:
    entries = sorted(
        [e for e in root.iterdir() if e.name not in IGNORE],
        key=lambda e: (not e.is_dir(), e.name.lower()),
    )
    lines = []
    for i, e in enumerate(entries):
        last = i == len(entries) - 1
        lines.append(f"{prefix}{'└── ' if last else '├── '}{e.name}{'/' if e.is_dir() else ''}")
        if e.is_dir():
            lines.extend(tree(e, prefix + ("    " if last else "│   ")))
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest")
    ap.add_argument("--root", default=".", help="project root (default: cwd)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--gitkeep", action="store_true", help="add .gitkeep to listed dirs that remain empty")
    args = ap.parse_args()

    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    with open(args.manifest, encoding="utf-8") as f:
        manifest = json.load(f)

    dirs = manifest.get("dirs", [])
    files = manifest.get("files", {})
    if not isinstance(dirs, list) or not isinstance(files, dict):
        print("manifest must have 'dirs' (list) and/or 'files' (object)", file=sys.stderr)
        return 2

    created_dirs, created_files, skipped = [], [], []

    for d in dirs:
        p = safe_join(root, d)
        if not p.exists():
            created_dirs.append(d)
            if not args.dry_run:
                p.mkdir(parents=True, exist_ok=True)

    for rel, content in files.items():
        p = safe_join(root, rel)
        if p.exists():
            skipped.append(rel)
            continue
        created_files.append(rel)
        if not args.dry_run:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content if isinstance(content, str) else json.dumps(content, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if args.gitkeep and not args.dry_run:
        for d in dirs:
            p = safe_join(root, d)
            if p.is_dir() and not any(p.iterdir()):
                (p / ".gitkeep").write_text("", encoding="utf-8")
                created_files.append(os.path.join(d, ".gitkeep"))

    tag = "[dry-run] " if args.dry_run else ""
    for d in created_dirs:
        print(f"{tag}DIR   {d}/")
    for f_ in created_files:
        print(f"{tag}FILE  {f_}")
    for s in skipped:
        print(f"{tag}SKIP  {s} (exists, not overwritten)")

    print(f"\n{root.resolve().name}/")
    print("\n".join(tree(root)))
    print(f"\n{len(created_dirs)} dirs, {len(created_files)} files created, {len(skipped)} skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
