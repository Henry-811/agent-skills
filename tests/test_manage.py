import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("manage", ROOT / "scripts/manage.py")
manage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manage)


class InstallationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agent skills ")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)

    def test_both_adapters_are_idempotent(self):
        for target in ("codex", "claude-code"):
            files, skills_root = manage.installation_plan(ROOT, self.home, target, rules=True, hook=True)
            count, _ = manage.install(files, skills_root, self.home)
            self.assertEqual(count, 13)
            self.assertEqual(manage.differences(files, skills_root), [])
            self.assertEqual(manage.install(files, skills_root, self.home)[0], 0)
            self.assertIn(b"# Global Development Methodology", next(data for path, data in files.items() if path.name in ("CLAUDE.md", "AGENTS.md")))

    def test_conflict_preflight_writes_nothing(self):
        files, skills_root = manage.installation_plan(ROOT, self.home, "codex")
        path = next(iter(files))
        path.parent.mkdir(parents=True)
        path.write_bytes(b"user edits")
        with self.assertRaisesRegex(ValueError, "Nothing was written"):
            manage.install(files, skills_root, self.home)
        self.assertEqual([p for p in self.home.rglob("*") if p.is_file()], [path])
        self.assertEqual(path.read_bytes(), b"user edits")

    def test_explicit_replace_backs_up_conflict(self):
        files, skills_root = manage.installation_plan(ROOT, self.home, "codex")
        manage.install(files, skills_root, self.home)
        path = next(iter(files))
        path.write_bytes(b"user edits")
        count, backup = manage.install(files, skills_root, self.home, replace=True)
        self.assertEqual(count, 1)
        self.assertEqual((backup / f"0-{path.name}").read_bytes(), b"user edits")
        self.assertEqual(path.read_bytes(), files[path])

    def test_extra_managed_file_is_not_deleted(self):
        files, skills_root = manage.installation_plan(ROOT, self.home, "codex")
        manage.install(files, skills_root, self.home)
        extra = skills_root / "dev-principles/local-note.md"
        extra.write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Extra files"):
            manage.install(files, skills_root, self.home, replace=True)
        self.assertEqual(extra.read_text(), "keep")

    def test_cli_does_not_touch_unrelated_settings(self):
        config = self.home / ".claude/settings.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({"custom": "keep"}))
        unrelated = self.home / ".claude/skills/unrelated/SKILL.md"
        unrelated.parent.mkdir(parents=True)
        unrelated.write_bytes(b"keep")
        for action in ("install", "check"):
            result = subprocess.run([sys.executable, str(ROOT / "scripts/manage.py"), action, "--target", "claude-code", "--home", str(self.home), "--rules", "--hook-script"], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(config.read_text()), {"custom": "keep"})
        self.assertEqual(unrelated.read_bytes(), b"keep")

    def test_custom_codex_home(self):
        custom = self.home / "custom-codex"
        files, skills_root = manage.installation_plan(ROOT, self.home, "codex", rules=True, hook=True, codex_home=custom)
        manage.install(files, skills_root, self.home)
        self.assertTrue((custom / "AGENTS.md").is_file())
        self.assertTrue((self.home / ".agents/skills/dev-principles/SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
