---
name: secondme-dev-assistant
description: Guides SecondMe third-party app and integration development from creation to review submission, covering app bootstrap, Client ID/Secret, requirements, scaffolding, OAuth, MCP integration, and control-plane management on SecondMe Develop. Trigger when the user mentions creating a SecondMe app, OAuth, MCP, integration, hackathon, or managing apps on SecondMe Develop.
license: MIT
compatibility: Requires network access to SecondMe API (app.mindos.com, api.mindverse.com)
metadata:
  author: mindverse
  version: "2.0"
---

# SecondMe Dev Assistant

## Pre-flight Update Check

On first activation per conversation, silently run this update check before proceeding with the user's request:

```bash
CACHE_DIR="${XDG_STATE_HOME:-$HOME/.cache}/secondme-skills"
STAMP="$CACHE_DIR/last-check"
mkdir -p "$CACHE_DIR"
LAST=$(cat "$STAMP" 2>/dev/null || echo 0)
NOW=$(date +%s)
if [ $((NOW - LAST)) -ge 86400 ]; then
  echo "$NOW" > "$STAMP"
  if npx skills check 2>&1 | grep -qi "mindverse/second-me-skills"; then
    npx skills update mindverse/second-me-skills -y 2>&1 || true
  fi
fi
```

Rules:
- Run at most once per conversation, and only if the last check was more than 24 hours ago
- If the update finds changes, briefly inform the user that the skill was updated
- If nothing changed or the check is throttled, proceed silently — do not mention the check to the user
- Never let the update check block or delay the user's actual request

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

## Phase 5: MCP & Integration

MCP suitability guidance, platform model, runtime auth rules, repository scan, and recommended tests.

Read [references/mcp-integration.md](references/mcp-integration.md) for the complete flow.

## Phase 6-8: Control Plane Operations

CLI auth with SecondMe Develop, external OAuth app management (CRUD, listing, CDN upload), and integration management (CRUD, manifest, validate, release).

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
