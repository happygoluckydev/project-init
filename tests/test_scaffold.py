"""Tests for scripts/scaffold.py and scripts/validate.py. Run: python3 -m unittest discover -s tests"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAFFOLD = ROOT / "scripts" / "scaffold.py"
VALIDATE = ROOT / "scripts" / "validate.py"


def run(script, *args):
    return subprocess.run([sys.executable, str(script), *map(str, args)], capture_output=True, text=True)


class ScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.manifest = self.base / "manifest.json"
        self.manifest.write_text(json.dumps({
            "dirs": ["src", "docs/adr", ".claude/skills"],
            "files": {
                "README.md": "# x\n",
                ".claude/settings.json": {"permissions": {"deny": ["Read(./.env)"]}},
            },
        }), encoding="utf-8")
        self.target = self.base / "proj"

    def tearDown(self):
        self.tmp.cleanup()

    def test_creates_dirs_and_files(self):
        r = run(SCAFFOLD, self.manifest, "--root", self.target)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.target / "docs/adr").is_dir())
        self.assertEqual((self.target / "README.md").read_text(), "# x\n")
        settings = json.loads((self.target / ".claude/settings.json").read_text())
        self.assertEqual(settings["permissions"]["deny"], ["Read(./.env)"])
        self.assertIn("3 dirs, 2 files created, 0 skipped", r.stdout)

    def test_never_overwrites(self):
        self.target.mkdir()
        (self.target / "README.md").write_text("keep me\n")
        r = run(SCAFFOLD, self.manifest, "--root", self.target)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.target / "README.md").read_text(), "keep me\n")
        self.assertIn("SKIP  README.md", r.stdout)

    def test_dry_run_touches_nothing(self):
        r = run(SCAFFOLD, self.manifest, "--root", self.target, "--dry-run", "--gitkeep")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(self.target.exists(), "dry-run must not create the root")
        self.assertIn("[dry-run] DIR   src/", r.stdout)
        self.assertIn("[dry-run] FILE  src/.gitkeep", r.stdout)

    def test_gitkeep_only_in_empty_dirs(self):
        r = run(SCAFFOLD, self.manifest, "--root", self.target, "--gitkeep")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.target / "src/.gitkeep").exists())
        self.assertFalse((self.target / ".claude/.gitkeep").exists())  # not listed, has children

    def test_rejects_path_escape(self):
        bad = self.base / "bad.json"
        bad.write_text(json.dumps({"dirs": ["../evil"]}))
        r = run(SCAFFOLD, bad, "--root", self.target)
        self.assertEqual(r.returncode, 2)
        self.assertIn("path escapes root", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertFalse((self.base / "evil").exists())
        self.assertFalse(self.target.exists(), "must abort before creating anything")

    def test_rejects_bad_manifest_shape(self):
        bad = self.base / "bad.json"
        bad.write_text(json.dumps({"dirs": "src"}))
        r = run(SCAFFOLD, bad, "--root", self.target)
        self.assertEqual(r.returncode, 2)
        self.assertIn("manifest must have", r.stderr)


class ValidateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / ".claude/skills/release").mkdir(parents=True)
        (self.root / ".claude/agents").mkdir()
        (self.root / ".claude/rules").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def test_passes_on_valid_project(self):
        self.write(".claude/skills/release/SKILL.md", '---\nname: release\ndescription: "Cut a release: bump, tag"\n---\n# body\n')
        self.write(".claude/agents/code-reviewer.md", '---\nname: code-reviewer\ndescription: "Review diffs"\n---\nbody\n')
        self.write(".claude/rules/db.md", '---\npaths:\n  - "src/db/**"\n---\n# db\n')
        self.write(".claude/settings.json", '{"permissions": {}}\n')
        self.write("CLAUDE.md", "# p\n" * 10)
        r = run(VALIDATE, "--root", self.root, "--no-tree")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("OK", r.stdout)

    def test_reports_problems(self):
        self.write(".claude/skills/release/SKILL.md", '---\nname: deploy\ndescription: ""\n---\n')
        self.write(".claude/agents/reviewer.md", '---\ndescription: "x"\n---\n')
        self.write(".claude/settings.json", "{not json")
        self.write("CLAUDE.md", "# p\n" * 5)
        r = run(VALIDATE, "--root", self.root, "--no-tree", "--max-claude-lines", "3")
        self.assertEqual(r.returncode, 1)
        for needle in ("name 'deploy' != 'release'", "description is empty", "require a 'name'", "invalid JSON", "5 lines > 3"):
            self.assertIn(needle, r.stdout)


if __name__ == "__main__":
    unittest.main()
