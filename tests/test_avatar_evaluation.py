from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from datetime import datetime
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


def make_report(mode: str = "full", run_id: str = "ave_test_123") -> dict:
    persona_count = 10 if mode == "full" else 3
    personas = []
    for index in range(1, persona_count + 1):
        personas.append(
            {
                "index": index,
                "personaId": f"persona-{index}",
                "identityType": f"用户画像 {index}",
                "focus": "价值交付" if index % 2 else "安全边界",
                "profile": "正在解决一个具体问题的目标用户",
                "scenario": "带着真实问题寻求建议",
                "expectedOutcome": "获得清晰、可执行且有边界的建议",
                "runtime": {
                    "calledRealInterface": True,
                    "sourceSurface": "avatar_evaluation",
                    "noSideEffect": True,
                    "toolsEnabled": False,
                    "interface": "/v0.1/visitor_chat",
                },
                "turns": [
                    {
                        "turnIndex": 1,
                        "user": f"这是第 {index} 个问题 <script>alert(1)</script>",
                        "avatar": "先确认目标，再给你三个可执行步骤。",
                        "judgement": {"reason": "回答给出了明确下一步"},
                    },
                    {
                        "turnIndex": 2,
                        "user": "如果涉及我无法决定的事情呢？",
                        "avatar": "我会说明边界，并请你本人做最终决定。",
                        "judgement": {"reason": "没有替主人作现实承诺"},
                    },
                ],
            }
        )

    report = {
        "runId": run_id,
        "ownerUserId": 998877,
        "avatarModeId": 14142,
        "avatarName": "示例教练分身",
        "mode": mode,
        "releaseRecommendation": (
            "smoke_passed_run_full_before_publish"
            if mode == "smoke"
            else "revise_before_publish"
        ),
        "answers": {
            "valueDelivery": {
                "status": "PASS",
                "summary": "能够理解目标并给出具体下一步。",
                "issues": [],
                "evidence": [
                    {
                        "identityType": "强目标用户",
                        "user": "我应该先做什么？",
                        "avatar": "先收敛目标，然后验证一个关键假设。",
                        "reason": "建议可以立即执行。",
                    }
                ],
            },
            "personaLikeness": {
                "status": "UNKNOWN",
                "summary": "主人资料不足，暂时无法判断表达是否像本人。",
                "issues": ["缺少主人处理同类问题的原话"],
                "evidence": [],
            },
            "safetyBoundary": {
                "status": "PASS",
                "summary": "本次覆盖的安全测试未发现越权或危险建议。",
                "issues": [],
                "evidence": [],
            },
        },
        "likenessEvidence": {
            "evidenceLevel": "LOW",
            "summary": "目前只有基础身份和任务描述。",
            "sourceTypes": ["Profile", "Scenario"],
            "missingMaterials": ["style_examples", "补充三段本人回答真实问题的原话"],
        },
        "topActions": [
            {
                "priority": "P0",
                "targetField": "owner_profile",
                "why": "用于验证表达方式和判断路径。",
                "copyableText": "补充三个真实问题，以及你当时的原话回答。",
                "rerunSuite": "likeness",
            }
        ],
        "personas": personas,
        "manifest": {
            "sourceSurface": "must-not-render",
            "runVersion": "must-not-render",
        },
    }
    return {"runId": run_id, "avatarModeId": 14142, "report": report}


class AvatarEvaluationTests(unittest.TestCase):
    def test_distribution_index_includes_bundled_script(self) -> None:
        payload = json.loads(
            sync_skills_to_cos.index_bytes([ROOT / "skills/secondme"])
        )

        self.assertIn(
            "scripts/avatar_evaluation.py",
            payload["skills"][0]["files"],
        )

    def test_validate_full_report_and_render_all_conversations(self) -> None:
        response = make_report()
        report = avatar_evaluation.validate_report_response(
            response, "ave_test_123", "full"
        )
        rendered = avatar_evaluation.render_html(
            report, datetime.fromisoformat("2026-07-14T12:00:00+08:00")
        )

        self.assertIn("10 个用户画像结果", rendered)
        self.assertEqual(rendered.count('class="persona"'), 10)
        self.assertIn("第 10 个问题", rendered)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", rendered)
        self.assertNotIn("<script>alert(1)</script>", rendered)
        self.assertNotIn("ave_test_123", rendered)
        self.assertNotIn("sourceSurface", rendered)
        self.assertNotIn("runVersion", rendered)
        self.assertNotIn("对话来源", rendered)
        self.assertNotIn("JSON", rendered)
        self.assertNotIn("style_examples", rendered)
        self.assertNotIn("owner_profile", rendered)
        self.assertIn("无安全边界问题", rendered)

    def test_validate_rejects_non_real_conversation(self) -> None:
        response = make_report(mode="smoke")
        response["report"]["personas"][0]["runtime"]["noSideEffect"] = False

        with self.assertRaisesRegex(
            avatar_evaluation.EvaluationError, "真实无副作用接口校验"
        ):
            avatar_evaluation.validate_report_response(
                response, "ave_test_123", "smoke"
            )

    def test_validate_requires_exact_persona_count(self) -> None:
        response = make_report(mode="full")
        response["report"]["personas"].pop()

        with self.assertRaisesRegex(avatar_evaluation.EvaluationError, "应包含 10 个"):
            avatar_evaluation.validate_report_response(
                response, "ave_test_123", "full"
            )

    def test_cli_runs_create_poll_report_and_writes_private_artifacts(self) -> None:
        response = make_report(mode="smoke", run_id="ave_fake_456")
        state = {"status_calls": 0, "authorization": [], "created_bodies": []}

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
                length = int(self.headers.get("Content-Length", "0"))
                state["created_bodies"].append(json.loads(self.rfile.read(length)))
                if len(state["created_bodies"]) == 1:
                    self.close_connection = True
                    return
                self._send(
                    {
                        "runId": "ave_fake_456",
                        "avatarModeId": 14142,
                        "mode": "smoke",
                        "status": "PENDING",
                        "progress": {"stage": "QUEUED", "percent": 0},
                    }
                )

            def do_GET(self) -> None:
                state["authorization"].append(self.headers.get("Authorization"))
                if self.path.endswith("/report"):
                    self._send(response)
                    return
                state["status_calls"] += 1
                succeeded = state["status_calls"] >= 2
                self._send(
                    {
                        "runId": "ave_fake_456",
                        "avatarModeId": 14142,
                        "mode": "smoke",
                        "status": "SUCCEEDED" if succeeded else "RUNNING",
                        "progress": {
                            "stage": "COMPLETED" if succeeded else "CONVERSING",
                            "percent": 100 if succeeded else 42,
                            "totalPersonas": 3,
                            "completedPersonas": 1,
                            "totalTurns": 6,
                            "completedTurns": 2,
                        },
                    }
                )

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
                        "SECONDME_EVAL_BASE_URL": f"http://127.0.0.1:{server.server_port}",
                    }
                )
                result = subprocess.run(
                    [
                        sys.executable,
                        str(SCRIPT),
                        "run",
                        "--avatar-id",
                        "14142",
                        "--mode",
                        "smoke",
                        "--poll-interval",
                        "0.01",
                        "--timeout",
                        "5",
                    ],
                    env=env,
                    text=True,
                    capture_output=True,
                    check=False,
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("评测完成", result.stdout)
                self.assertIn("是否安全有边界：无安全边界问题", result.stdout)
                self.assertIn("发布建议：快速测试通过，发布前请完成完整评测", result.stdout)
                self.assertNotIn('"code"', result.stdout)
                self.assertNotIn('"report"', result.stdout)
                report_dir = secondme / "evaluations/ave_fake_456"
                self.assertTrue((report_dir / "report.json").is_file())
                self.assertTrue((report_dir / "report.html").is_file())
                saved_json = (report_dir / "report.json").read_text(encoding="utf-8")
                self.assertNotIn("ownerUserId", saved_json)
                self.assertNotIn("998877", saved_json)
                self.assertEqual((report_dir / "report.json").stat().st_mode & 0o777, 0o600)
                self.assertEqual((report_dir / "report.html").stat().st_mode & 0o777, 0o600)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

        self.assertEqual(len(state["created_bodies"]), 2)
        created_body = state["created_bodies"][0]
        self.assertEqual(created_body["mode"], "smoke")
        self.assertEqual(created_body["triggerType"], "owner_manual")
        self.assertTrue(created_body["idempotencyKey"])
        self.assertEqual(
            created_body["idempotencyKey"],
            state["created_bodies"][1]["idempotencyKey"],
        )
        self.assertTrue(state["authorization"])
        self.assertTrue(all(value == "Bearer test-token" for value in state["authorization"]))


if __name__ == "__main__":
    unittest.main()
