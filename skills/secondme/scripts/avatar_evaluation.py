#!/usr/bin/env python3
"""Run an owner-authenticated avatar evaluation and render its owner report."""

from __future__ import annotations

import argparse
import html
import http.client
import json
import os
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


BASE_URLS = {
    "prod": "https://api.mindverse.com/gate/lab",
    "pre": "https://mindos-prek8s.mindverse.ai/gate/lab",
}
REQUEST_ATTEMPTS = 3
TERMINAL_STATUSES = {"SUCCEEDED", "FAILED"}
ANSWER_CONFIG = (
    ("valueDelivery", "是否交付价值"),
    ("personaLikeness", "像不像我"),
    ("safetyBoundary", "是否安全有边界"),
)
STATUS_LABELS = {
    "PASS": "通过",
    "WARN": "需要改进",
    "FAIL": "未通过",
    "UNKNOWN": "证据不足",
}
SAFETY_LABELS = {
    "PASS": "无安全边界问题",
    "WARN": "发现安全边界问题",
    "FAIL": "发现安全边界问题",
    "UNKNOWN": "本次安全检查未完成",
}
RELEASE_LABELS = {
    "publishable": "可发布",
    "revise_before_publish": "修改后再发布",
    "do_not_publish": "暂不发布",
}
ACTION_TARGET_LABELS = {
    "scenarioPrompt": "分身任务与边界",
    "scenario_prompt": "分身任务与边界",
    "opening": "开场白",
    "welcomeNote": "欢迎语",
    "welcome_note": "欢迎语",
    "profile": "主人基础资料",
    "owner_profile": "主人基础资料",
    "keyMemory": "关键记忆",
    "key_memory": "关键记忆",
    "notes": "主人资料",
    "styleExamples": "主人表达样例",
    "style_examples": "主人表达样例",
    "judgementExamples": "主人判断案例",
    "judgement_examples": "主人判断案例",
    "boundaries": "主人边界说明",
    "boundary_rules": "安全边界",
}
FRIENDLY_TERMS = (
    ("judgement_examples", "判断案例"),
    ("style_examples", "表达样例"),
    ("boundary_rules", "边界规则"),
    ("owner_profile", "主人资料"),
    ("value_delivery", "价值交付"),
    ("persona_likeness", "像不像我"),
    ("safety_boundary", "安全边界"),
    ("scenarioPrompt", "分身任务与边界"),
    ("owner", "主人"),
)
PRIVATE_JSON_KEYS = {
    "accessToken",
    "access_token",
    "ownerUserId",
    "owner_user_id",
    "token",
    "userId",
    "user_id",
}
STAGE_LABELS = {
    "QUEUED": "等待开始",
    "PLANNING": "生成测试画像",
    "CONVERSING": "进行多轮对话",
    "JUDGING": "分析结果",
    "COMPLETED": "已完成",
    "FAILED": "运行失败",
}


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


def _escape(value: Any, default: str = "") -> str:
    return html.escape(_text(value, default), quote=True)


def _friendly(value: Any, default: str = "") -> str:
    result = _text(value, default)
    for source, target in FRIENDLY_TERMS:
        result = result.replace(source, target)
    return result


def _friendly_escape(value: Any, default: str = "") -> str:
    return html.escape(_friendly(value, default), quote=True)


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


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
        "User-Agent": "secondme-skill-avatar-evaluation/1",
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


def _error_message(raw: bytes) -> str:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return ""
    if not isinstance(payload, dict):
        return ""
    return _text(payload.get("message") or payload.get("msg"))


def _write_private_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _without_private_fields(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _without_private_fields(item)
            for key, item in value.items()
            if key not in PRIVATE_JSON_KEYS
        }
    if isinstance(value, list):
        return [_without_private_fields(item) for item in value]
    return value


def _write_private_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _progress_line(summary: dict[str, Any]) -> str:
    progress = _dict(summary.get("progress"))
    stage = _text(progress.get("stage"), "QUEUED")
    percent = progress.get("percent", 0)
    try:
        percent = max(0, min(100, int(percent)))
    except (TypeError, ValueError):
        percent = 0
    parts = [f"评测进行中：{STAGE_LABELS.get(stage, stage)} {percent}%"]
    completed_personas = progress.get("completedPersonas")
    total_personas = progress.get("totalPersonas")
    if isinstance(completed_personas, int) and isinstance(total_personas, int) and total_personas:
        parts.append(f"画像 {completed_personas}/{total_personas}")
    completed_turns = progress.get("completedTurns")
    total_turns = progress.get("totalTurns")
    if isinstance(completed_turns, int) and isinstance(total_turns, int) and total_turns:
        parts.append(f"对话 {completed_turns}/{total_turns} 轮")
    return "，".join(parts)


def _poll(
    base_url: str,
    token: str,
    run_id: str,
    initial: dict[str, Any] | None,
    interval: float,
    timeout: float,
) -> dict[str, Any]:
    started = time.monotonic()
    current = initial or {}
    last_line = ""
    while True:
        status = _text(current.get("status"))
        if status in TERMINAL_STATUSES:
            if status == "FAILED":
                code = _text(current.get("errorCode"), "评测运行失败")
                message = _text(current.get("errorMessage"))
                detail = f"：{message}" if message else ""
                raise EvaluationError(f"评测未完成（{code}）{detail}")
            return current

        line = _progress_line(current)
        if line != last_line:
            print(line, flush=True)
            last_line = line

        if time.monotonic() - started >= timeout:
            raise EvaluationError(
                f"评测仍在后台运行。稍后可用 run id {run_id} 继续获取结果。"
            )
        time.sleep(interval)
        current = _api_request(
            "GET",
            f"{base_url}/api/secondme/avatar/evaluations/{run_id}",
            token,
        )


def validate_report_response(
    response: dict[str, Any],
    expected_run_id: str,
    expected_mode: str,
) -> dict[str, Any]:
    report = response.get("report")
    if not isinstance(report, dict):
        raise EvaluationError("完整报告缺少 report 数据。")
    if _text(response.get("runId")) != expected_run_id:
        raise EvaluationError("完整报告与本次评测任务不匹配。")
    if _text(report.get("runId")) != expected_run_id:
        raise EvaluationError("报告内容与本次评测任务不匹配。")
    if _text(report.get("mode")) != expected_mode:
        raise EvaluationError("报告模式与本次评测任务不匹配。")

    answers = _dict(report.get("answers"))
    for key, title in ANSWER_CONFIG:
        answer = _dict(answers.get(key))
        if _text(answer.get("status")) not in STATUS_LABELS:
            raise EvaluationError(f"报告缺少“{title}”的有效结论。")
        if not _text(answer.get("summary")):
            raise EvaluationError(f"报告缺少“{title}”的结论说明。")

    personas = _list(report.get("personas"))
    expected_count = 3 if expected_mode == "smoke" else 10
    if len(personas) != expected_count:
        raise EvaluationError(
            f"报告不完整：{expected_mode} 应包含 {expected_count} 个用户画像，实际为 {len(personas)} 个。"
        )
    for index, raw_persona in enumerate(personas, start=1):
        persona = _dict(raw_persona)
        turns = _list(persona.get("turns"))
        if not 2 <= len(turns) <= 5:
            raise EvaluationError(f"报告不完整：第 {index} 个画像的对话应为 2 至 5 轮。")
        runtime = _dict(persona.get("runtime"))
        if not (
            runtime.get("calledRealInterface") is True
            and runtime.get("sourceSurface") == "avatar_evaluation"
            and runtime.get("noSideEffect") is True
            and runtime.get("toolsEnabled") is False
        ):
            raise EvaluationError(f"报告不可信：第 {index} 个画像未通过真实无副作用接口校验。")
        for turn_index, raw_turn in enumerate(turns, start=1):
            turn = _dict(raw_turn)
            if not _text(turn.get("user")) or not _text(turn.get("avatar")):
                raise EvaluationError(f"报告不完整：第 {index} 个画像第 {turn_index} 轮缺少对话。")
    return report


def _status_label(key: str, status: str) -> str:
    if key == "safetyBoundary":
        return SAFETY_LABELS.get(status, "本次安全检查未完成")
    return STATUS_LABELS.get(status, "证据不足")


def _status_class(status: str) -> str:
    return {
        "PASS": "pass",
        "WARN": "warn",
        "FAIL": "fail",
        "UNKNOWN": "unknown",
    }.get(status, "unknown")


def _render_list(items: list[Any], empty: str = "本次没有发现具体问题。") -> str:
    rendered = "".join(f"<li>{_escape(item)}</li>" for item in items if _text(item))
    return f"<ul>{rendered}</ul>" if rendered else f'<p class="muted">{_escape(empty)}</p>'


def _render_evidence(evidence: list[Any]) -> str:
    rows: list[str] = []
    for item in evidence:
        entry = _dict(item)
        user = _text(entry.get("user"))
        avatar = _text(entry.get("avatar"))
        reason = _text(entry.get("reason") or entry.get("summary"))
        identity = _text(entry.get("identityType") or entry.get("personaName"), "测试用户")
        conversation = ""
        if user:
            conversation += f'<div class="quote user"><b>用户</b><p>{_escape(user)}</p></div>'
        if avatar:
            conversation += f'<div class="quote avatar"><b>分身</b><p>{_escape(avatar)}</p></div>'
        if not conversation and not reason:
            continue
        rows.append(
            '<div class="evidence">'
            f'<div class="evidence-title">{_escape(identity)}</div>'
            f"{conversation}"
            f'{f"<p class=reason>{_escape(reason)}</p>" if reason else ""}'
            "</div>"
        )
    if not rows:
        return '<p class="muted">本次结论没有附加单独的证据摘录，可在下方完整对话中查看。</p>'
    return "".join(rows)


def _render_answers(report: dict[str, Any]) -> str:
    answers = _dict(report.get("answers"))
    cards: list[str] = []
    for key, title in ANSWER_CONFIG:
        answer = _dict(answers.get(key))
        status = _text(answer.get("status"), "UNKNOWN")
        cards.append(
            f'<section class="answer { _status_class(status) }">'
            '<div class="answer-head">'
            f"<h2>{title}</h2>"
            f'<span class="status">{_escape(_status_label(key, status))}</span>'
            "</div>"
            f'<p class="summary">{_escape(answer.get("summary"), "本次没有形成有效说明。")}</p>'
            '<details><summary>问题与证据</summary>'
            '<h3>发现的问题</h3>'
            f'{_render_list(_list(answer.get("issues")))}'
            '<h3>判断证据</h3>'
            f'{_render_evidence(_list(answer.get("evidence")))}'
            "</details></section>"
        )
    return "".join(cards)


def _render_likeness(report: dict[str, Any]) -> str:
    evidence = _dict(report.get("likenessEvidence"))
    level = _text(evidence.get("evidenceLevel"), "UNKNOWN")
    level_label = {
        "HIGH": "资料较充分",
        "MEDIUM": "资料基本可用",
        "LOW": "资料不足",
        "UNKNOWN": "尚未确认资料充分度",
    }.get(level, "尚未确认资料充分度")
    source_types = [_text(item) for item in _list(evidence.get("sourceTypes")) if _text(item)]
    source_note = f"已使用 {len(source_types)} 类主人资料。" if source_types else "尚未识别到可验证的主人资料类型。"
    return (
        '<section class="band"><div class="section-head">'
        '<div><p class="eyebrow">判断基础</p><h2>主人资料充分度</h2></div>'
        f'<span class="material-level">{_escape(level_label)}</span></div>'
        f'<p>{_friendly_escape(evidence.get("summary"), source_note)}</p>'
        f'<p class="muted">{_escape(source_note)}</p>'
        '<h3>建议补充</h3>'
        f'{_render_list([_friendly(item) for item in _list(evidence.get("missingMaterials"))], "目前没有额外补充项。")}'
        "</section>"
    )


def _render_actions(report: dict[str, Any]) -> str:
    actions = _list(report.get("topActions"))
    if not actions:
        content = '<p class="muted">本次没有生成明确的修改动作。</p>'
    else:
        rows: list[str] = []
        for index, raw_action in enumerate(actions, start=1):
            action = _dict(raw_action)
            copyable = _text(action.get("copyableText"))
            target = _text(action.get("targetField"), "分身设定")
            target = ACTION_TARGET_LABELS.get(target, target)
            rows.append(
                '<article class="action">'
                f'<span class="action-index">{index}</span><div>'
                f'<h3>{_escape(target)}</h3>'
                f'<p>{_friendly_escape(action.get("why"), "根据本次对话证据进行调整。")}</p>'
                f'{f"<div class=copyable>{_friendly_escape(copyable)}</div>" if copyable else ""}'
                "</div></article>"
            )
        content = "".join(rows)
    return (
        '<section class="band"><p class="eyebrow">下一步</p><h2>优先改进动作</h2>'
        f"{content}</section>"
    )


def _judgement_text(value: Any) -> str:
    judgement = _dict(value)
    preferred = ("reason", "summary", "result", "label")
    texts = [_text(judgement.get(key)) for key in preferred if _text(judgement.get(key))]
    return "；".join(dict.fromkeys(texts))


def _render_personas(report: dict[str, Any]) -> str:
    personas = _list(report.get("personas"))
    overview: list[str] = []
    details: list[str] = []
    for index, raw_persona in enumerate(personas, start=1):
        persona = _dict(raw_persona)
        identity = _text(persona.get("identityType"), f"用户画像 {index}")
        focus = _text(persona.get("focus"), "综合体验")
        scenario = _text(persona.get("scenario"), "未提供场景说明")
        turns = _list(persona.get("turns"))
        overview.append(
            '<div class="persona-row">'
            f'<span class="persona-number">{index:02d}</span><div><h3>{_escape(identity)}</h3>'
            f'<p>{_friendly_escape(focus)} · {len(turns)} 轮对话</p></div></div>'
        )
        turn_rows: list[str] = []
        for turn_index, raw_turn in enumerate(turns, start=1):
            turn = _dict(raw_turn)
            judgement = _judgement_text(turn.get("judgement"))
            turn_rows.append(
                '<div class="turn">'
                f'<div class="turn-label">第 {turn_index} 轮</div>'
                f'<div class="quote user"><b>用户</b><p>{_escape(turn.get("user"))}</p></div>'
                f'<div class="quote avatar"><b>分身</b><p>{_escape(turn.get("avatar"))}</p></div>'
                f'{f"<p class=reason><b>判断：</b>{_escape(judgement)}</p>" if judgement else ""}'
                "</div>"
            )
        details.append(
            '<details class="persona">'
            f'<summary><span>{index:02d}</span><div><b>{_escape(identity)}</b>'
            f'<small>{_friendly_escape(focus)} · {len(turns)} 轮</small></div></summary>'
            '<div class="persona-body">'
            '<div class="persona-context">'
            f'<div><b>用户情况</b><p>{_escape(persona.get("profile"), "未提供")}</p></div>'
            f'<div><b>测试场景</b><p>{_escape(scenario)}</p></div>'
            f'<div><b>预期结果</b><p>{_escape(persona.get("expectedOutcome"), "未提供")}</p></div>'
            "</div>"
            f'{"".join(turn_rows)}</div></details>'
        )
    return (
        '<section class="band personas"><p class="eyebrow">真实测试证据</p>'
        f'<h2>{len(personas)} 个用户画像结果</h2>'
        '<p class="muted">先查看全貌，需要时展开任一画像的完整多轮对话。</p>'
        f'<div class="persona-overview">{"".join(overview)}</div>'
        f'<div class="persona-details">{"".join(details)}</div></section>'
    )


def render_html(report: dict[str, Any], generated_at: datetime | None = None) -> str:
    generated_at = generated_at or datetime.now().astimezone()
    avatar_name = _text(report.get("avatarName"), "未命名分身")
    mode = _text(report.get("mode"), "full")
    mode_label = "快速测试" if mode == "smoke" else "完整评测"
    recommendation = RELEASE_LABELS.get(
        _text(report.get("releaseRecommendation")), "暂不发布"
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_escape(avatar_name)} · 分身评测报告</title>
<style>
:root{{--ink:#17212b;--muted:#667383;--line:#dce3e8;--paper:#fff;--bg:#f3f6f7;--green:#16794b;--green-bg:#e9f6ef;--amber:#9a6200;--amber-bg:#fff3d8;--red:#b73333;--red-bg:#fdecec;--blue:#2c608d;}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;line-height:1.65;letter-spacing:0}} main{{max-width:1080px;margin:0 auto;padding:40px 24px 72px}} h1,h2,h3,p{{margin-top:0}} h1{{font-size:36px;line-height:1.25;margin-bottom:12px}} h2{{font-size:23px;line-height:1.35;margin-bottom:14px}} h3{{font-size:16px;margin-bottom:8px}} .hero{{background:#173b4d;color:#fff;padding:38px 40px;margin-bottom:24px;border-radius:6px}} .hero p{{color:#dbe7ec;margin-bottom:0}} .meta{{display:flex;flex-wrap:wrap;gap:10px 18px;margin-top:22px;align-items:center}} .recommendation{{background:#fff;color:#173b4d;font-weight:700;padding:7px 12px;border-radius:4px}} .answers{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin-bottom:24px}} .answer,.band{{background:var(--paper);border:1px solid var(--line);border-radius:6px}} .answer{{padding:24px;border-top-width:4px}} .answer.pass{{border-top-color:var(--green)}} .answer.warn{{border-top-color:var(--amber)}} .answer.fail{{border-top-color:var(--red)}} .answer.unknown{{border-top-color:var(--blue)}} .answer-head,.section-head{{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}} .status,.material-level{{font-size:14px;font-weight:700;white-space:nowrap;padding:4px 9px;border-radius:4px;background:#edf2f4}} .pass .status{{color:var(--green);background:var(--green-bg)}} .warn .status{{color:var(--amber);background:var(--amber-bg)}} .fail .status{{color:var(--red);background:var(--red-bg)}} .unknown .status{{color:var(--blue)}} .summary{{font-size:17px;min-height:82px}} details{{border-top:1px solid var(--line);padding-top:14px}} summary{{cursor:pointer;font-weight:700}} details[open]>summary{{margin-bottom:18px}} ul{{padding-left:22px}} .band{{padding:30px 32px;margin-bottom:24px}} .eyebrow{{font-size:13px;text-transform:uppercase;color:var(--blue);font-weight:700;margin-bottom:5px}} .muted{{color:var(--muted)}} .evidence{{border-top:1px solid var(--line);padding:14px 0}} .evidence-title{{font-weight:700;margin-bottom:8px}} .quote{{padding:12px 14px;margin:8px 0;background:#f5f7f8;border-left:3px solid #8795a3}} .quote.avatar{{border-left-color:var(--green);background:#f3f8f5}} .quote p{{white-space:pre-wrap;margin:4px 0 0}} .reason{{color:var(--muted);margin:10px 0 0}} .action{{display:grid;grid-template-columns:34px 1fr;gap:14px;padding:18px 0;border-top:1px solid var(--line)}} .action-index,.persona-number{{font-weight:800;color:var(--blue)}} .copyable{{padding:12px 14px;background:#f5f7f8;white-space:pre-wrap;border-radius:4px}} .persona-overview{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));border-top:1px solid var(--line);margin:20px 0 28px}} .persona-row{{display:grid;grid-template-columns:38px 1fr;gap:10px;padding:16px 12px;border-bottom:1px solid var(--line)}} .persona-row h3,.persona-row p{{margin:0}} .persona-row p{{color:var(--muted);font-size:14px}} .persona-details{{display:grid;gap:10px}} details.persona{{border:1px solid var(--line);border-radius:5px;padding:0}} .persona summary{{display:grid;grid-template-columns:42px 1fr;gap:8px;padding:17px 18px;list-style:none}} .persona summary::-webkit-details-marker{{display:none}} .persona summary span{{font-weight:800;color:var(--blue)}} .persona summary small{{display:block;color:var(--muted);font-weight:400}} .persona-body{{padding:0 20px 20px}} .persona-context{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;background:#f5f7f8;padding:16px;margin-bottom:16px}} .persona-context p{{margin:4px 0 0}} .turn{{padding:18px 0;border-top:1px solid var(--line)}} .turn-label{{font-weight:800;margin-bottom:8px}} footer{{color:var(--muted);text-align:center;font-size:13px;padding-top:14px}}
@media(max-width:820px){{main{{padding:20px 14px 48px}}.hero{{padding:28px 24px}}h1{{font-size:29px}}.answers{{grid-template-columns:1fr}}.summary{{min-height:0}}.persona-overview,.persona-context{{grid-template-columns:1fr}}.band{{padding:24px 20px}}}}
</style>
</head>
<body><main>
<header class="hero">
  <p>分身评测报告</p>
  <h1>{_escape(avatar_name)}</h1>
  <p>这份报告基于真实用户画像与分身的多轮对话，回答主人最关心的三个问题。</p>
  <div class="meta"><span class="recommendation">{_escape(recommendation)}</span><span>{_escape(mode_label)}</span><span>{generated_at.strftime("%Y-%m-%d %H:%M")}</span></div>
</header>
<div class="answers">{_render_answers(report)}</div>
{_render_likeness(report)}
{_render_actions(report)}
{_render_personas(report)}
<footer>评测结论仅覆盖本次测试中的场景与对话；修改分身后请重新运行评测。</footer>
</main></body></html>
"""


def _save_report(root: Path, run_id: str, response: dict[str, Any], report: dict[str, Any]) -> tuple[Path, Path]:
    run_dir = root.expanduser() / run_id
    json_path = run_dir / "report.json"
    html_path = run_dir / "report.html"
    _write_private_json(json_path, _without_private_fields(response))
    _write_private_text(html_path, render_html(report))
    return json_path, html_path


def _print_result(report: dict[str, Any], html_path: Path) -> None:
    print("\n评测完成")
    answers = _dict(report.get("answers"))
    for key, title in ANSWER_CONFIG:
        status = _text(_dict(answers.get(key)).get("status"), "UNKNOWN")
        print(f"- {title}：{_status_label(key, status)}")
    recommendation = RELEASE_LABELS.get(
        _text(report.get("releaseRecommendation")), "暂不发布"
    )
    print(f"- 发布建议：{recommendation}")
    print(f"- 完整报告：{html_path}")


def _run(args: argparse.Namespace) -> None:
    base_url = _base_url(args.environment)
    token = _read_access_token(args.credentials)
    root = args.output_dir.expanduser()
    idempotency_key = str(uuid.uuid4())
    request_state = root / "requests" / f"{idempotency_key}.json"
    state = {
        "avatarModeId": args.avatar_id,
        "mode": args.mode,
        "environment": args.environment,
        "idempotencyKey": idempotency_key,
        "createdAt": datetime.now().astimezone().isoformat(),
    }
    _write_private_json(request_state, state)
    print(f"开始{ '快速测试' if args.mode == 'smoke' else '完整评测' }。", flush=True)
    created = _api_request(
        "POST",
        f"{base_url}/api/secondme/avatar/{args.avatar_id}/evaluations",
        token,
        {
            "mode": args.mode,
            "triggerType": "owner_manual",
            "idempotencyKey": idempotency_key,
        },
    )
    run_id = _text(created.get("runId"))
    if not run_id:
        raise EvaluationError("评测创建成功但未返回 run id。")
    state["runId"] = run_id
    _write_private_json(request_state, state)
    completed = _poll(base_url, token, run_id, created, args.poll_interval, args.timeout)
    mode = _text(completed.get("mode"), args.mode)
    response = _api_request(
        "GET",
        f"{base_url}/api/secondme/avatar/evaluations/{run_id}/report",
        token,
    )
    report = validate_report_response(response, run_id, mode)
    _, html_path = _save_report(root, run_id, response, report)
    _print_result(report, html_path)


def _resume(args: argparse.Namespace) -> None:
    base_url = _base_url(args.environment)
    token = _read_access_token(args.credentials)
    summary = _api_request(
        "GET",
        f"{base_url}/api/secondme/avatar/evaluations/{args.run_id}",
        token,
    )
    completed = _poll(base_url, token, args.run_id, summary, args.poll_interval, args.timeout)
    mode = _text(completed.get("mode"))
    if mode not in ("smoke", "full"):
        raise EvaluationError("评测状态缺少有效模式。")
    response = _api_request(
        "GET",
        f"{base_url}/api/secondme/avatar/evaluations/{args.run_id}/report",
        token,
    )
    report = validate_report_response(response, args.run_id, mode)
    _, html_path = _save_report(args.output_dir.expanduser(), args.run_id, response, report)
    _print_result(report, html_path)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="运行小己分身真实评测并生成主人报告")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--environment",
        choices=sorted(BASE_URLS),
        default="prod",
        help="服务环境；pre 仅用于内部预发布验证",
    )
    common.add_argument(
        "--credentials",
        type=Path,
        default=Path("~/.secondme/credentials"),
        help=argparse.SUPPRESS,
    )
    common.add_argument(
        "--output-dir",
        type=Path,
        default=Path("~/.secondme/evaluations"),
        help="报告保存目录",
    )
    common.add_argument("--poll-interval", type=float, default=5.0, help=argparse.SUPPRESS)
    common.add_argument("--timeout", type=float, default=1800.0, help="最长等待秒数")

    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", parents=[common], help="创建并等待一份新评测")
    run.add_argument("--avatar-id", type=int, required=True)
    run.add_argument("--mode", choices=("smoke", "full"), default="smoke")
    run.set_defaults(handler=_run)

    resume = subparsers.add_parser("resume", parents=[common], help="继续等待已有评测")
    resume.add_argument("--run-id", required=True)
    resume.set_defaults(handler=_resume)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if getattr(args, "avatar_id", 1) <= 0:
        print("错误：avatar id 必须是正整数。", file=sys.stderr)
        return 2
    if args.poll_interval <= 0 or args.timeout <= 0:
        print("错误：轮询间隔和等待时间必须大于 0。", file=sys.stderr)
        return 2
    try:
        args.handler(args)
    except EvaluationError as exc:
        print(f"评测未完成：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
