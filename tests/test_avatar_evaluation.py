from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/secondme/scripts/avatar_evaluation.py"
SPEC = importlib.util.spec_from_file_location("avatar_evaluation", SCRIPT)
assert SPEC and SPEC.loader
avatar_evaluation = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(avatar_evaluation)
SYNC_SPEC = importlib.util.spec_from_file_location(
    "sync_skills_to_cos", ROOT / "scripts/sync_skills_to_cos.py"
)
assert SYNC_SPEC and SYNC_SPEC.loader
sync_skills_to_cos = importlib.util.module_from_spec(SYNC_SPEC)
sys.modules[SYNC_SPEC.name] = sync_skills_to_cos
SYNC_SPEC.loader.exec_module(sync_skills_to_cos)


class AvatarEvaluationTests(unittest.TestCase):
    def test_docs_execute_the_bundled_script_from_the_skill_directory(self) -> None:
        skill = (ROOT / "skills/secondme/SKILL.md").read_text(encoding="utf-8")
        reference = (
            ROOT / "skills/secondme/references/avatar-evaluation.md"
        ).read_text(encoding="utf-8")

        command = 'python3 "${SKILL_DIR}/scripts/avatar_evaluation.py"'
        self.assertIn(command, skill)
        self.assertIn(command, reference)
        self.assertIn("不得把脚本复制到用户工程", skill)

    def test_distribution_index_includes_bundled_script(self) -> None:
        payload = json.loads(
            sync_skills_to_cos.index_bytes([ROOT / "skills/secondme"])
        )

        self.assertIn(
            "scripts/avatar_evaluation.py",
            payload["skills"][0]["files"],
        )

    def test_validate_accepts_second_me_web_url(self) -> None:
        self.assertEqual(
            avatar_evaluation._validate_evaluation_url(
                "https://beta.second-me.cn/avatars/evaluations/ave-123"
            ),
            "https://beta.second-me.cn/avatars/evaluations/ave-123",
        )

    def test_validate_rejects_external_web_url(self) -> None:
        with self.assertRaisesRegex(
            avatar_evaluation.EvaluationError, "无效的评测页面地址"
        ):
            avatar_evaluation._validate_evaluation_url(
                "https://example.com/avatars/evaluations/ave-123"
            )

    def test_cli_does_not_expose_a_mode_choice(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "run", "--help"],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("--mode", result.stdout)

    def test_cli_creates_once_and_prints_web_url_without_polling(self) -> None:
        state = {
            "authorization": [],
            "created_bodies": [],
            "get_calls": 0,
            "user_agents": [],
        }

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, _format: str, *_args: object) -> None:
                return

            def _send(self, payload: dict, status: int = 200) -> None:
                raw = json.dumps({"code": 0, "data": payload}).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def do_POST(self) -> None:
                state["authorization"].append(self.headers.get("Authorization"))
                state["user_agents"].append(self.headers.get("User-Agent"))
                length = int(self.headers.get("Content-Length", "0"))
                state["created_bodies"].append(json.loads(self.rfile.read(length)))
                if len(state["created_bodies"]) == 1:
                    self.close_connection = True
                    return
                self._send(
                    {
                        "runId": "ave_fake_456",
                        "avatarModeId": 14142,
                        "mode": "full",
                        "status": "PENDING",
                        "progress": {"stage": "QUEUED", "percent": 0},
                        "evaluationUrl": (
                            f"http://127.0.0.1:{self.server.server_port}"
                            "/avatars/evaluations/ave_fake_456"
                        ),
                    }
                )

            def do_GET(self) -> None:
                state["get_calls"] += 1
                self._send({})

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as home:
                secondme = Path(home) / ".secondme"
                secondme.mkdir()
                credentials = secondme / "credentials"
                credentials.write_text(
                    json.dumps({"accessToken": "test-token"}), encoding="utf-8"
                )
                env = os.environ.copy()
                env.update(
                    {
                        "HOME": home,
                        "SECONDME_SKILL_TESTING": "1",
                        "SECONDME_EVAL_BASE_URL": (
                            f"http://127.0.0.1:{server.server_port}"
                        ),
                    }
                )
                result = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "run",
                        "--avatar-id",
                        "14142",
                    ],
                    env=env,
                    text=True,
                    capture_output=True,
                    check=False,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("分身评测已开始", result.stdout)
                self.assertIn(
                    "/avatars/evaluations/ave_fake_456", result.stdout
                )
                self.assertNotIn('"code"', result.stdout)
                self.assertFalse((secondme / "evaluations").exists())
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(state["get_calls"], 0)
        self.assertEqual(len(state["created_bodies"]), 2)
        first_body = state["created_bodies"][0]
        second_body = state["created_bodies"][1]
        self.assertEqual(first_body["mode"], "full")
        self.assertEqual(first_body["triggerType"], "owner_manual")
        self.assertTrue(first_body["idempotencyKey"])
        self.assertEqual(
            first_body["idempotencyKey"], second_body["idempotencyKey"]
        )
        self.assertTrue(state["authorization"])
        self.assertTrue(
            all(value == "Bearer test-token" for value in state["authorization"])
        )
        self.assertTrue(
            all(
                value == "secondme-skill-avatar-evaluation/3.6.1"
                for value in state["user_agents"]
            )
        )


if __name__ == "__main__":
    unittest.main()
