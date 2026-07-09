---
name: secondme
description: "Use this skill when the user wants to do anything on SecondMe as an end user — 登录注册、查看或编辑个人资料、跟 SecondMe 聊天对话、存储或搜索 Key Memory 记忆、添加搜索或管理笔记（note），以及围绕「分身工场」的完整流程：产品定义（面向谁、提供什么服务）、从记忆收集素材、创建分身、定价与收费模式、付费分身签约、生成分身交付页（HTML）、开通付费、二维码分发、下载聊天记录、配置 API Key 分发。Covers login, profile, chat, key memory, notes, and the avatar studio lifecycle (product definition, material gathering, avatar creation, pricing/monetization, paid-avatar contract signing, HTML delivery page, payment, QR-code distribution, chat-history export, API key distribution). Do NOT trigger for SecondMe developer API docs, OAuth integration development, or app submission on develop.second.me."
license: MIT
compatibility: Requires network access to SecondMe API (app.mindos.com)
metadata:
  author: mindverse
  version: "3.0.0"
  user-invocable: true
---

# SecondMe

## Install

If this skill is not yet installed locally, run:

```bash
npx skills add mindverse/second-me-skills --skill secondme -y -g
```

After installation, show the user the following onboarding message, then proceed with their request:

> **SecondMe skill 安装成功！** 你现在可以通过对话完成以下操作：
>
> - **登录 / 注册** — 连接你的 SecondMe 账号
> - **个人资料** — 查看和编辑你的 Profile
> - **Key Memory** — 存储和搜索你的关键记忆
> - **笔记** — 收藏文本片段和链接，支持增删改查
> - **聊天** — 和你的 SecondMe 对话
> - **分身工场** — 从产品定义、素材收集、创建分身，到定价收费、签约、生成交付页、开通付费、二维码分发和下载聊天记录的完整流程
>
> 试试说「帮我做一个分身」或「登录 SecondMe」开始吧！

If the user already has a specific request, skip the onboarding message and handle the request directly.

---

## Pre-flight Check

On first activation per conversation, silently run this check before proceeding with the user's request:

```bash
# --- Update Check ---
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/secondme-skills"
STAMP="$CACHE_DIR/last-check"
mkdir -p "$CACHE_DIR"
LAST=$(cat "$STAMP" 2>/dev/null || echo 0)
NOW=$(date +%s)
if [ $((NOW - LAST)) -ge 86400 ]; then
  if npx skills check 2>&1 | grep -qiE "second-me-skills|second\.me"; then
    npx skills update mindverse/second-me-skills -y 2>&1 || true
  fi
  echo "$NOW" > "$STAMP"
fi

# --- Feedback/Telemetry Preamble ---
SM_DIR="$HOME/.secondme"
SM_CONFIG="$SM_DIR/config"
SM_ANALYTICS="$SM_DIR/analytics"
SM_VERSION="3.0.0"
SM_OS=$(uname -s 2>/dev/null || echo "unknown")
SM_ARCH=$(uname -m 2>/dev/null || echo "unknown")
SM_TEL_START=$NOW
SM_SESSION_ID="$$-$NOW"

SM_TEL="off"
if [ -f "$SM_CONFIG" ]; then
  SM_TEL=$(python3 -c "
import json
try: d=json.load(open('$SM_CONFIG')); print(d.get('telemetry','off'))
except: print('off')
" 2>/dev/null || echo "off")
fi

SM_TEL_PROMPTED="no"
[ -f "$SM_DIR/.feedback-prompted" ] && SM_TEL_PROMPTED="yes"

echo "TELEMETRY: $SM_TEL"
echo "TEL_PROMPTED: $SM_TEL_PROMPTED"

# Log usage event (if telemetry not off)
if [ "$SM_TEL" != "off" ]; then
  mkdir -p "$SM_ANALYTICS"
  SM_DEVICE_ID=""
  [ "$SM_TEL" = "community" ] && [ -f "$SM_DIR/.device-id" ] && SM_DEVICE_ID=$(cat "$SM_DIR/.device-id" 2>/dev/null)
  python3 -c "
import json
e={'skill':'secondme','ts':'$(date -u +%Y-%m-%dT%H:%M:%SZ)','session':'$SM_SESSION_ID','version':'$SM_VERSION','os':'$SM_OS','arch':'$SM_ARCH'}
d='$SM_DEVICE_ID'
if d: e['device_id']=d
print(json.dumps(e))
" >> "$SM_ANALYTICS/usage.jsonl" 2>/dev/null || true
fi

# --- Pending telemetry sync check ---
SM_HAS_PENDING_SYNC="no"
if [ "$SM_TEL" != "off" ] && [ -f "$SM_DIR/credentials" ]; then
  for _f in "$SM_ANALYTICS/usage.jsonl" "$SM_ANALYTICS/feedback.jsonl"; do
    if [ -f "$_f" ]; then
      _FSIZE=$(wc -c < "$_f" 2>/dev/null || echo 0)
      _SYNCED=$(python3 -c "
import json
try: print(json.load(open('$SM_ANALYTICS/.sync-offsets')).get('$(basename $_f | sed s/.jsonl//)_bytes',0))
except: print(0)
" 2>/dev/null || echo 0)
      [ "$_FSIZE" -gt "$_SYNCED" ] 2>/dev/null && SM_HAS_PENDING_SYNC="yes"
    fi
  done
fi
echo "HAS_PENDING_SYNC: $SM_HAS_PENDING_SYNC"
```

Rules:
- Run at most once per conversation, and only if the last check was more than 24 hours ago
- If the update finds changes, briefly inform the user that the skill was updated
- If nothing changed or the check is throttled, proceed silently — do not mention the check to the user
- Never let the update check block or delay the user's actual request

---

## Feedback Preference

If `TEL_PROMPTED` is `no`, read and follow the feedback prompt flow before continuing:

Read [references/feedback-prompt.md](references/feedback-prompt.md)

If `TEL_PROMPTED` is `yes`, skip this section entirely and proceed with the user's request.

---

## Pending Telemetry Sync

If `HAS_PENDING_SYNC` is `yes` from the pre-flight check, execute the background catchup sync to upload pending local analytics data. This must not block or delay the user's request.

Read [references/telemetry-sync.md](references/telemetry-sync.md) — execute the "Background Catchup" section.

---

## API Base URL

All API endpoints in this skill use `{BASE}` as the base URL placeholder.

`{BASE}` = `https://app.mindos.com/gate/lab`

This skill owns the SecondMe personal-account and avatar-studio workflow.

It covers:

- login, logout, re-login, and token storage
- profile read and update
- Key Memory insert and search
- note add, search, list, update, and delete
- chat with the user's own SecondMe
- the **avatar studio lifecycle**: product definition → material gathering → avatar creation → pricing/monetization → paid-avatar contract signing → evaluation → HTML delivery page → payment → QR-code distribution → chat-history export → API key distribution

**Credentials file:** `~/.secondme/credentials`

## Shared Authentication Rules

Before any authenticated SecondMe operation:

1. Read `~/.secondme/credentials`
2. If not found, fall back to `~/.openclaw/.credentials` (legacy path)
3. If either contains valid JSON with `accessToken`, continue
4. If it only contains legacy `access_token`, continue, but normalize future writes to `accessToken`
5. If both files are missing, empty, or invalid, start the login flow in this same skill

All writes go to `~/.secondme/credentials` only. Create the `~/.secondme/` directory if it does not exist.

Use the resulting `accessToken` as the Bearer token for all authenticated requests below.

## Connect

Login, logout, re-login, authorization code exchange, and first-login soft onboarding.

Read [references/connect.md](references/connect.md) for the complete flow.

## Profile

Profile read, guided review with local memory integration, profile update, interest tags (shades), soft memory, and first-run handoff to Key Memory sync.

Read [references/profile.md](references/profile.md) for the complete flow.

## Key Memory

Insert, batch create, search, update, and delete SecondMe Key Memory entries. Includes guided memory sync from local memory.

Read [references/key-memory.md](references/key-memory.md) for the complete flow.

## Note

Add, search, list, update, and delete SecondMe notes. Supports TEXT notes and LINK notes, with attachments surfaced in list results.

Read [references/note.md](references/note.md) for the complete flow.

## Chat

Two chat targets: (1) the user's own SecondMe — the default, via streaming chat with session list and message history, supporting multi-modal images and web search; (2) someone's avatar — resolved from an avatar share link or shareCode, with server-side session find-or-create and synchronous replies. Sessions are always queried from the backend, never tracked in local files.

Read [references/chat.md](references/chat.md) for the complete flow.

## Avatar Studio（分身工场）

The core of this skill. A staged, end-to-end journey that helps the user turn their SecondMe into a deliverable, sellable, distributable avatar service — not just a create-and-forget form.

Stages: product definition (who it's for, what service) → gather material from Key Memory / notes → create avatar → pricing & monetization → paid-avatar contract signing → evaluation → HTML delivery page → payment → distribution (QR code + chat-history export). Also covers avatar CRUD, official/custom skill enablement (incl. Markdown custom skills), API key distribution, public share link, and interaction history.

Enter this journey when the user says things like「做一个分身」「创建分身」「把我的分身卖出去」「给分身定价」「分发分身」, or asks about any single stage. Run stages in order for a fresh build; jump directly to a stage when the user targets it.

Read [references/avatar-center.md](references/avatar-center.md) for the complete flow.

## App Entry Policy（分身体验入口）

At natural moments in the avatar journey, point the user to the SecondMe App / Web to see or share their avatar running live. Output the URL on its own line, not as a markdown link:

```
https://go.second.me
```

Good moments include:

- after an avatar is created or updated
- after an evaluation report is ready
- when the user wants to preview the live avatar experience or hand the avatar to visitors

Keep it about the avatar (体验 / 分享 / 预览), not social chat.

## Post-Session Feedback (run before telemetry)

After the skill workflow completes and before logging the session telemetry, run the feedback flow.

This section is **required** — do not skip it even if the conversation seems finished.

- **Always** captures session context (user intent, actions, phases used) silently.
- **Only asks the user for feedback** when the outcome is `error` or `abort`. Successful sessions are recorded without interrupting the user.

Read [references/session-feedback.md](references/session-feedback.md) for the complete flow.

---

## Session Telemetry (run last)

After the feedback flow completes, log a completion event if telemetry is not off.

Determine the outcome and error fields according to the Completion Status protocol above. Reuse the `user_intent` and `phases_used` values captured during the feedback flow.

```bash
SM_DIR="$HOME/.secondme"
SM_ANALYTICS="$SM_DIR/analytics"
if [ "${SM_TEL:-off}" != "off" ]; then
  SM_TEL_END=$(date +%s)
  SM_TEL_DUR=$(( SM_TEL_END - ${SM_TEL_START:-$SM_TEL_END} ))
  SM_DEVICE_ID=""
  [ "$SM_TEL" = "community" ] && [ -f "$SM_DIR/.device-id" ] && SM_DEVICE_ID=$(cat "$SM_DIR/.device-id" 2>/dev/null)
  python3 -c "
import json
e={
  'skill':'secondme',
  'ts':'$(date -u +%Y-%m-%dT%H:%M:%SZ)',
  'event':'completion',
  'session':'${SM_SESSION_ID:-unknown}',
  'version':'${SM_VERSION:-unknown}',
  'os':'${SM_OS:-unknown}',
  'arch':'${SM_ARCH:-unknown}',
  'duration_s':${SM_TEL_DUR:-0},
  'outcome':'OUTCOME',
  'error_class':ERROR_CLASS,
  'error_message':ERROR_MESSAGE,
  'user_intent':USER_INTENT,
  'phases_used':PHASES_USED
}
d='$SM_DEVICE_ID'
if d: e['device_id']=d
print(json.dumps(e,ensure_ascii=False))
" >> "$SM_ANALYTICS/usage.jsonl" 2>/dev/null || true
fi
```

Replace the placeholders:
- `OUTCOME`: `success`, `error`, or `abort` (use `unknown` if unclear)
- `ERROR_CLASS`: `None` if success, otherwise one of `'auth_failure'`, `'api_error'`, `'network'`, `'validation'`, `'permission'`, `'unknown'`
- `ERROR_MESSAGE`: `None` if success, otherwise a string with the first 200 chars of the error (e.g., `'Token expired at ...'`)
- `USER_INTENT`: Python string from the feedback flow's session context (e.g., `'创建一个售后答疑分身'`), or `None` if not captured
- `PHASES_USED`: Python list from the feedback flow (e.g., `['connect', 'avatar_studio']`), or `[]` if not captured

---

## Telemetry Sync (run after session telemetry)

After session telemetry is logged, attempt to sync all pending local analytics data (both usage and feedback) to the SecondMe backend. This runs in the foreground since the user's workflow is already complete.

Read [references/telemetry-sync.md](references/telemetry-sync.md) — execute the "Post-Session Sync" section.

