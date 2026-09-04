#!/usr/bin/env python3
"""scripts/scaffold.py のスモークテスト（API 不要、数秒）。

確認すること:
    1. assets/manifest.example.json を空ディレクトリに展開すると、dirs と files がすべてできる
    2. もう一度展開しても既存ファイルを上書きしない（SKIP になり、内容が変わらない）
    3. --dry-run では何も作らない
    4. ルートの外に出るパスは拒否される
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD = ROOT / "scripts" / "scaffold.py"
MANIFEST = ROOT / "assets" / "manifest.example.json"


def run(*args):
    return subprocess.run([sys.executable, str(SCAFFOLD), *args], capture_output=True, text=True)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "proj"

        r = run(str(MANIFEST), "--root", str(target), "--dry-run")
        assert r.returncode == 0, r.stderr
        assert not target.exists() or not any(target.iterdir()), "--dry-run が何か作った"

        r = run(str(MANIFEST), "--root", str(target))
        assert r.returncode == 0, r.stderr
        for d in manifest["dirs"]:
            assert (target / d).is_dir(), f"dir がない: {d}"
        for f in manifest["files"]:
            assert (target / f).is_file(), f"file がない: {f}"

        readme = target / "README.md"
        readme.write_text("changed\n", encoding="utf-8")
        r = run(str(MANIFEST), "--root", str(target))
        assert r.returncode == 0, r.stderr
        assert "SKIP  README.md" in r.stdout, "既存ファイルが SKIP になっていない"
        assert readme.read_text(encoding="utf-8") == "changed\n", "既存ファイルが上書きされた"

        bad = Path(tmp) / "bad.json"
        bad.write_text(json.dumps({"files": {"../escape.txt": "x"}}), encoding="utf-8")
        r = run(str(bad), "--root", str(target))
        assert r.returncode != 0, "ルート外のパスが拒否されなかった"
        assert not (Path(tmp) / "escape.txt").exists()

    print("smoke_scaffold: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
