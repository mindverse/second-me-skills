---
name: secondme-dev-assistant
description: "Use when user wants to develop on the SecondMe platform (second.me, develop.second.me). Triggers: building SecondMe third-party apps (第三方应用/外部应用), SecondMe OAuth login integration (Client ID/Secret, token exchange), MCP integration for SecondMe, Agent Memory API, Act stream API, app scaffolding, review submission, or hackathon/黑客松 projects targeting SecondMe. Covers the full developer lifecycle from app creation and credentials to release. NOT for casual SecondMe usage like browsing profiles, adding friends, or social features — only for building and integrating with SecondMe as a developer platform."
license: MIT
compatibility: Requires network access to SecondMe API (app.mindos.com, api.mindverse.com)
metadata:
  author: mindverse
  version: "2.1.0"
---

# SecondMe Dev Assistant

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
SM_VERSION="2.1.0"
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
e={'skill':'secondme-dev-assistant','ts':'$(date -u +%Y-%m-%dT%H:%M:%SZ)','session':'$SM_SESSION_ID','version':'$SM_VERSION','os':'$SM_OS','arch':'$SM_ARCH'}
d='$SM_DEVICE_ID'
if d: e['device_id']=d
print(json.dumps(e))
" >> "$SM_ANALYTICS/usage.jsonl" 2>/dev/null || true
fi
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

This is the single entry skill for SecondMe developer work.

Use it for the full lifecycle:

- creating a SecondMe app on [develop.second.me](https://develop.second.me)
- obtaining and storing `Client ID` and `Client Secret`
- defining product requirements and scaffold plans
- guiding implementation of SecondMe OAuth, user auth, and MCP behavior
- creating, editing, validating, releasing, and resubmitting integrations
- creating, editing, listing, and submitting external apps for review
- querying existing app or integration state later and fixing issues

Do not treat this skill as only an MCP manifest helper. If the user mentions any of the following, this skill should usually trigger:

- "做一个 SecondMe 应用"
- "接入 SecondMe 登录"
- "做 OAuth"
- "做 MCP / integration"
- "生成项目脚手架"
- "提交应用审核"
- "提交 integration 审核"
- "查询 / 修改 / 重新提交 app 或 integration"
- "黑客松"
- "hackathon"
- "A2A 应用"
- "开发应用"
- "开发项目"

Early trigger rule:

- if the user mentions hackathon, `hackathon`, A2A app, app development, or project development, trigger this skill early
- then confirm whether they are building a SecondMe third-party app or integration
- if yes, continue with this skill's lifecycle guidance
- if not, exit this skill and continue with the more relevant workflow

## Scope

This skill is a developer assistant, not a blind code generator.

It should:

- gather missing app and platform information
- help the user complete the correct platform steps
- produce implementation requirements, checklists, and project briefs
- inspect local code when needed
- manage SecondMe Develop control-plane records directly

It should not:

- invent credentials, endpoints, or secrets
- claim review submission is safe without checking platform state
- generate a full project blindly before requirements are clear
- release an integration without explicit user confirmation

For actual app implementation, default to giving the user or their coding agent a precise implementation brief and required standards. Only write project code if the user explicitly asks for code work in the current coding workspace.

## Trigger Map

Treat these as the same family of tasks:

- `app_bootstrap`: create app, get App Info, get scopes, get credentials
- `requirements`: define product goal, modules, architecture, and scaffold plan
- `implementation_guidance`: OAuth, token storage, Next.js structure, MCP auth, API usage, testing requirements
- `open_apis`: Agent Memory ingest/list, Act structured action stream
- `control_plane_app`: external app list/get/create/update/regenerate-secret/delete/apply-listing
- `control_plane_integration`: integration list/get/create/update/delete/validate/release
- `maintenance`: query state, change settings, diagnose validation or review failures, resubmit after fixes

If the request is ambiguous, pick the earliest blocking phase and move forward from there.

## Operating Modes

### 1. Full Build Lifecycle

Use when the user is starting or expanding a SecondMe app.

Flow:

1. bootstrap the app through SecondMe Develop APIs by default
2. collect and normalize credentials and scopes
3. clarify requirements
4. produce scaffold and implementation guidance
5. help configure app metadata and integration metadata
6. validate and submit
7. support later maintenance and resubmission

### 2. Control-Plane Only

Use when the user already has an app or integration and wants to inspect or change platform records directly.

Do not force requirement discovery or scaffold planning in this mode.

### 3. Repository-Aware Guidance

Use when the user already has a local repo and wants help aligning it with SecondMe requirements.

Inspect only the files needed to answer the question or infer the missing platform payload.

## Phase 1 & 2: App Bootstrap and Client Secret

Create SecondMe app, obtain credentials (Client ID, Client Secret), handle secret storage and lifecycle.

Read [references/app-bootstrap.md](references/app-bootstrap.md) for the complete flow.

## Phase 3: Requirements & Scaffold Plan

Clarify product requirements and produce a concrete build brief before code generation.

Read [references/requirements-scaffold.md](references/requirements-scaffold.md) for the complete flow.

## Phase 4: Implementation Guidance

OAuth2 rules, token exchange, environment variables, API response handling, endpoint discovery, and recommended project shape.

Read [references/implementation-guidance.md](references/implementation-guidance.md) for the complete flow.

## Open APIs Reference

Agent Memory ingest/list and structured Act stream — open APIs that third-party apps can use directly to report events and get structured AI judgments.

Read [references/open-apis.md](references/open-apis.md) for the complete flow.

## Phase 5: MCP & Integration

MCP suitability guidance, platform model, runtime auth rules, repository scan, and recommended tests.

Read [references/mcp-integration.md](references/mcp-integration.md) for the complete flow.

## Phase 6-8: Control Plane Operations

Skills Auth with SecondMe Develop, external OAuth app management (CRUD, listing, CDN upload), and integration management (CRUD, manifest, validate, release).

Read [references/control-plane.md](references/control-plane.md) for the complete flow.

## Phase 9: Release & Maintenance

Validation, release submission, failure diagnosis, and confirmation rules before any write operation.

Read [references/release-maintenance.md](references/release-maintenance.md) for the complete flow.

## Response Style

- compact
- transparent
- precise
- security-first

Always distinguish:

- `confirmed`
- `inferred`
- `missing`

Never repeat raw secret values back to the user.

## Operational Rules

- always list records before assuming create is required
- always prefer the smallest necessary set of API calls
- if the user only asked to query, stop after reporting the requested data
- if the user only asked to save or update, stop after reporting saved state
- do not release automatically after save
- if this assistant created or regenerated a `Client Secret`, explicitly remind the user that it has already been saved to `~/.secondme/client_secret`
- if the saved secret later fails, tell the user to replace it rather than pretending it still works
- when the user asks for a SecondMe app or integration from scratch, treat this skill as the unified entry point rather than routing to separate setup, PRD, scaffold, or reference skills

## Session Telemetry (run last)

After the skill workflow completes, log a completion event if telemetry is not off.

Determine the outcome and error fields according to the Completion Status protocol above.

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
  'skill':'secondme-dev-assistant',
  'ts':'$(date -u +%Y-%m-%dT%H:%M:%SZ)',
  'event':'completion',
  'session':'${SM_SESSION_ID:-unknown}',
  'version':'${SM_VERSION:-unknown}',
  'os':'${SM_OS:-unknown}',
  'arch':'${SM_ARCH:-unknown}',
  'duration_s':${SM_TEL_DUR:-0},
  'outcome':'OUTCOME',
  'error_class':ERROR_CLASS,
  'error_message':ERROR_MESSAGE
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

