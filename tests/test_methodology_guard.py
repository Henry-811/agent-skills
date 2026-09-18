import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks" / "methodology_guard.py"
CASES = [
    ("我们讨论 skill 设计", set()),
    ("讨论 git rebase 的区别", set()),
    ("你好，今天怎么样", set()),
    ("修复登录 bug", {"dev-principles"}),
    ("修复bug", {"dev-principles"}),
    ("review代码", {"dev-principles"}),
    ("修改代码中的空值判断", {"dev-principles"}),
    ("审查代码，不改代码", {"dev-principles"}),
    ("不改代码但要审查代码", {"dev-principles"}),
    ("不改代码，只修改配置", {"dev-principles"}),
    ("这次不要写代码，仅讨论 hook 设计", set()),
    ("只讨论不实现这个 API", {"product-check"}),
    ("想做新产品，先明确目标用户", {"concept-exploration"}),
    ("新增收藏功能并实现代码", {"concept-exploration", "product-check", "dev-principles"}),
    ("实现新功能：用户收藏", {"concept-exploration", "product-check", "dev-principles"}),
    ("设计新 feature 的业务规则", {"concept-exploration", "product-check"}),
    ("修改 API 的权限校验", {"product-check", "dev-principles"}),
    ("Review the code; do not edit code", {"dev-principles"}),
    ("Discuss hook design only, no code changes", set()),
    ("Implement a new feature", {"concept-exploration", "product-check", "dev-principles"}),
]


def invoke(command, payload, shell=False):
    result = subprocess.run(command, input=payload, capture_output=True, timeout=5, shell=shell)
    if result.returncode:
        raise AssertionError(result.stderr.decode("utf-8", errors="replace"))
    output = result.stdout.decode("utf-8-sig").strip()
    return (json.loads(output) if output else None), result.stderr.decode("utf-8")


def selected_skills(response):
    if response is None:
        return set()
    context = response["hookSpecificOutput"]["additionalContext"]
    return {name for name in ("concept-exploration", "product-check", "dev-principles")
            if f"`{name}`" in context}


class MethodologyGuardTests(unittest.TestCase):
    def test_prompt_matrix(self):
        for prompt, expected in CASES:
            with self.subTest(prompt=prompt):
                response, stderr = invoke(
                    [sys.executable, str(HOOK)],
                    json.dumps({"prompt": prompt}, ensure_ascii=False).encode("utf-8"),
                )
                self.assertEqual(stderr, "")
                self.assertEqual(selected_skills(response), expected)
                if expected:
                    self.assertEqual(response["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")

    def test_empty_input(self):
        for payload in ({}, {"prompt": ""}, {"prompt": "   "}):
            response, stderr = invoke([sys.executable, str(HOOK)], json.dumps(payload).encode())
            self.assertIsNone(response)
            self.assertEqual(stderr, "")

    def test_utf8_bom_and_legacy_prompt(self):
        payload = json.dumps({"user_prompt": "审查代码，不改代码"}, ensure_ascii=False)
        response, stderr = invoke([sys.executable, str(HOOK)], payload.encode("utf-8-sig"))
        self.assertEqual(selected_skills(response), {"dev-principles"})
        self.assertEqual(stderr, "")

    def test_bad_input_is_visible_and_nonblocking(self):
        for payload in (b"{", b"[]", b"null", b'{"prompt":123}', b'{"prompt":0}', b'{"prompt":false}', b'{"prompt":[]}'):
            response, stderr = invoke([sys.executable, str(HOOK)], payload)
            self.assertIn("methodology-guard hook failed", stderr)
            self.assertIn("systemMessage", response)

    @unittest.skipUnless(os.name == "nt", "Windows hook command")
    def test_codex_adapter_command(self):
        config_path = ROOT / "adapters" / "codex" / "hooks.example.json"
        config = json.loads(config_path.read_text(encoding="utf-8-sig"))
        handlers = config["hooks"]["UserPromptSubmit"]
        commands = [hook.get("commandWindows") or hook["command"]
                    for group in handlers for hook in group["hooks"]
                    if hook.get("type") == "command" and "methodology_guard.py" in hook.get("commandWindows", hook.get("command", ""))]
        self.assertEqual(len(commands), 1)
        with tempfile.TemporaryDirectory(prefix="agent skills ") as directory:
            host = Path(directory)
            (host / "hooks").mkdir()
            (host / "hooks/methodology_guard.py").write_bytes(HOOK.read_bytes())
            env = {**os.environ, "CODEX_HOME": str(host)}
            for prompt, expected in CASES:
                with self.subTest(prompt=prompt):
                    result = subprocess.run(commands[0], input=json.dumps({"prompt": prompt}, ensure_ascii=False).encode("utf-8"), shell=True, env=env, capture_output=True, timeout=5)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stderr, b"")
                    response = json.loads(result.stdout) if result.stdout else None
                    self.assertEqual(selected_skills(response), expected)


if __name__ == "__main__":
    unittest.main()
