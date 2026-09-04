#!/usr/bin/env python3
"""Create a directory/file skeleton from a JSON manifest without overwriting anything.

Usage:
    python3 scaffold.py manifest.json [--root DIR] [--dry-run] [--gitkeep]

Manifest format:
    {
      "dirs":  ["src", "tests", ".claude/skills"],
      "files": {"README.md": "# name\n", ".claude/settings.json": {"permissions": {}}}
    }
    A file value that is not a string is written as pretty-printed JSON.

Behaviour:
    - Directories are created recursively (mkdir -p).
    - Files are written only if they do not exist; existing files are reported as SKIP.
    - With --gitkeep, directories listed in "dirs" that are still empty get a .gitkeep.
      Off by default: dirs you will fill later with other tools would otherwise keep a stray .gitkeep.
    - --dry-run touches nothing (not even --root) and only reports what would happen.
    - Paths that escape --root (e.g. "../x" or absolute paths) are rejected with exit code 2.
    - Prints a tree of everything under --root at the end (ignoring node_modules/.git/venvs).

Exit codes: 0 ok, 2 bad manifest or unsafe path.
"""
import argparse
import json
import os
import sys
from pathlib import Path

IGNORE = {"node_modules", ".git", ".venv", "venv", "__pycache__", "dist", "build", ".next"}


def safe_join(root: Path, rel: str) -> Path:
    """Resolve rel under root, refusing anything that escapes root."""
    root_r = root.resolve()
    p = (root_r / rel).resolve()
    if p != root_r and root_r not in p.parents:
        raise ValueError(f"path escapes root: {rel}")
    return p


def tree(root: Path, prefix: str = "") -> list:
    if not root.is_dir():
        return []
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


def load_manifest(path: str):
    with open(path, encoding="utf-8") as f:
        manifest = json.load(f)
    dirs = manifest.get("dirs", [])
    files = manifest.get("files", {})
    if not isinstance(dirs, list) or not isinstance(files, dict):
        raise ValueError("manifest must have 'dirs' (list) and/or 'files' (object)")
    return dirs, files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("manifest")
    ap.add_argument("--root", default=".", help="project root (default: cwd)")
    ap.add_argument("--dry-run", action="store_true", help="report only; create nothing")
    ap.add_argument("--gitkeep", action="store_true", help="add .gitkeep to listed dirs that remain empty")
    args = ap.parse_args()

    root = Path(args.root)
    try:
        dirs, files = load_manifest(args.manifest)
        # Validate every path before touching the filesystem, so a bad entry aborts cleanly.
        dir_paths = [(d, safe_join(root, d)) for d in dirs]
        file_paths = [(rel, safe_join(root, rel)) for rel in files]
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"scaffold: {e}", file=sys.stderr)
        return 2

    if not args.dry_run:
        root.mkdir(parents=True, exist_ok=True)

    created_dirs, created_files, skipped = [], [], []

    for d, p in dir_paths:
        if not p.exists():
            created_dirs.append(d)
            if not args.dry_run:
                p.mkdir(parents=True, exist_ok=True)

    for rel, p in file_paths:
        if p.exists():
            skipped.append(rel)
            continue
        created_files.append(rel)
        if not args.dry_run:
            content = files[rel]
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(
                content if isinstance(content, str) else json.dumps(content, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

    if args.gitkeep:
        for d, p in dir_paths:
            if args.dry_run:
                # Would be empty if it doesn't exist yet or currently has no entries.
                if not p.exists() or (p.is_dir() and not any(p.iterdir())):
                    created_files.append(os.path.join(d, ".gitkeep"))
            elif p.is_dir() and not any(p.iterdir()):
                (p / ".gitkeep").write_text("", encoding="utf-8")
                created_files.append(os.path.join(d, ".gitkeep"))

    tag = "[dry-run] " if args.dry_run else ""
    for d in created_dirs:
        print(f"{tag}DIR   {d}/")
    for f_ in created_files:
        print(f"{tag}FILE  {f_}")
    for s in skipped:
        print(f"{tag}SKIP  {s} (exists, not overwritten)")

    if root.is_dir():
        print(f"\n{root.resolve().name}/")
        print("\n".join(tree(root)))
    print(f"\n{len(created_dirs)} dirs, {len(created_files)} files created, {len(skipped)} skipped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
