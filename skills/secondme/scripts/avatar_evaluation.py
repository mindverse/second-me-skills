#!/usr/bin/env python3
"""Start an owner-authenticated avatar evaluation and print its Web URL."""

from __future__ import annotations

import argparse
import http.client
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any


BASE_URLS = {
    "prod": "https://api.mindverse.com/gate/lab",
    "pre": "https://mindos-prek8s.mindverse.ai/gate/lab",
}
REQUEST_ATTEMPTS = 3
EVALUATION_MODE = "full"


class EvaluationError(RuntimeError):
    """A user-actionable evaluation failure."""


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip() or default
    if isinstance(value, (int, float, bool)):
        return str(value)
    return default


def _base_url(environment: str) -> str:
    if os.environ.get("SECONDME_SKILL_TESTING") == "1":
        test_url = os.environ.get("SECONDME_EVAL_BASE_URL", "").rstrip("/")
        if test_url:
            return test_url
    return BASE_URLS[environment]


def _read_access_token(credentials_path: Path) -> str:
    candidates = [credentials_path.expanduser()]
    legacy = Path("~/.openclaw/.credentials").expanduser()
    if legacy not in candidates:
        candidates.append(legacy)

    for path in candidates:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            continue
        token = _text(payload.get("accessToken") or payload.get("access_token"))
        if token:
            return token
    raise EvaluationError("未找到有效登录凭据，请先运行小己登录流程。")


def _error_message(raw: bytes) -> str:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return ""
    if not isinstance(payload, dict):
        return ""
    return _text(payload.get("message") or payload.get("msg"))


def _api_request(
    method: str,
    url: str,
    token: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = None
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "secondme-skill-avatar-evaluation/3.6.1",
    }
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    raw = b""
    for attempt in range(1, REQUEST_ATTEMPTS + 1):
        request = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                raw = response.read()
            break
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            if exc.code >= 500 and attempt < REQUEST_ATTEMPTS:
                time.sleep(attempt)
                continue
            message = _error_message(raw) or f"HTTP {exc.code}"
            if exc.code == 401:
                raise EvaluationError("登录已失效，请重新登录后继续评测。") from exc
            raise EvaluationError(f"评测接口请求失败：{message}") from exc
        except (urllib.error.URLError, http.client.HTTPException, OSError) as exc:
            if attempt < REQUEST_ATTEMPTS:
                time.sleep(attempt)
                continue
            reason = getattr(exc, "reason", exc)
            raise EvaluationError(f"无法连接评测服务：{reason}") from exc

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise EvaluationError("评测服务返回了无法识别的响应。") from exc
    if not isinstance(result, dict):
        raise EvaluationError("评测服务返回格式不正确。")
    code = result.get("code")
    if code not in (None, 0, "0"):
        if code in (401, "401"):
            raise EvaluationError("登录已失效，请重新登录后继续评测。")
        message = _text(result.get("message") or result.get("msg"), "未知错误")
        raise EvaluationError(f"评测服务拒绝了请求：{message}")
    data = result.get("data", result)
    if not isinstance(data, dict):
        raise EvaluationError("评测服务缺少结果数据。")
    return data


def _validate_evaluation_url(value: Any) -> str:
    url = _text(value)
    if not url:
        raise EvaluationError("评测已创建，但服务没有返回评测页面地址。")

    parsed = urllib.parse.urlparse(url)
    testing = os.environ.get("SECONDME_SKILL_TESTING") == "1"
    valid_host = parsed.hostname == "second-me.cn" or bool(
        parsed.hostname and parsed.hostname.endswith(".second-me.cn")
    )
    if not testing and (parsed.scheme != "https" or not valid_host):
        raise EvaluationError("评测服务返回了无效的评测页面地址。")
    if not parsed.path.startswith("/avatars/evaluations/"):
        raise EvaluationError("评测服务返回了无效的评测页面地址。")
    return url


def _run(args: argparse.Namespace) -> None:
    base_url = _base_url(args.environment)
    token = _read_access_token(args.credentials)
    idempotency_key = str(uuid.uuid4())
    created = _api_request(
        "POST",
        f"{base_url}/api/secondme/avatar/{args.avatar_id}/evaluations",
        token,
        {
            "mode": EVALUATION_MODE,
            "triggerType": "owner_manual",
            "idempotencyKey": idempotency_key,
        },
    )
    evaluation_url = _validate_evaluation_url(created.get("evaluationUrl"))

    print("分身评测已开始。")
    print("评测进度和完整报告将在网页中更新：")
    print(evaluation_url)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="启动小己分身真实评测")
    run = parser.add_subparsers(dest="command", required=True).add_parser(
        "run", help="创建一份新评测"
    )
    run.add_argument("--avatar-id", type=int, required=True)
    run.add_argument(
        "--environment",
        choices=sorted(BASE_URLS),
        default="prod",
        help="服务环境；pre 仅用于内部预发布验证",
    )
    run.add_argument(
        "--credentials",
        type=Path,
        default=Path("~/.secondme/credentials"),
        help=argparse.SUPPRESS,
    )
    run.set_defaults(handler=_run)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.avatar_id <= 0:
        print("错误：avatar id 必须是正整数。", file=sys.stderr)
        return 2
    try:
        args.handler(args)
    except EvaluationError as exc:
        print(f"评测未启动：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
