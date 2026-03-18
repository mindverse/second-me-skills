---
name: secondme-dev-assistant
description: Use when the user wants to configure, create, or update a SecondMe Skill/MCP integration from a local project, or needs help exposing existing project capabilities through MCP.
---

# SecondMe Dev Assistant

This skill turns a local project into a live SecondMe integration. It scans the repository to infer MCP-backed integration fields, identifies suitable functions to expose as tools if no MCP server exists yet, helps the user define and implement the MCP-facing surface, handles the CLI OAuth flow, and calls the official save and release APIs.

## Use This Skill For

- Creating or updating integrations from local code and configuration
- Analyzing whether an existing project is suitable for MCP exposure
- Building a draft manifest and submitting it to SecondMe Develop after the user confirms it
- Helping teammates fill complex integration fields without hand-writing JSON manifests

Do not use this skill to guess production secrets, invent missing configurations without user confirmation, or bypass the user's explicit approval for risky fields.

## Invocation Defaults

- Display name: `SecondMe Builder Skill`
- Short description: `Find MCP code in a project, help expose missing MCP capabilities, then save the integration`
- Default prompt: `Use $secondme-dev-assistant to scan this project, infer MCP fields, help expose any missing MCP capabilities, save the integration, then ask whether to release it for SecondMe review.`
- Implicit invocation: Allowed

## Workflow

### 1. Scan The Current Project

Read only the files necessary to infer the integration or analyze MCP suitability.

Search order:

1. metadata: `README*`, `package.json`, `pyproject.toml`, `Cargo.toml`
2. MCP config: `mcp.json`, `*.mcp.*`, server configs, deployment manifests
3. tool registration: entrypoints, decorators, router registrations, SDK setup
4. auth and env: `.env*`, example envs, secret templates, auth middleware
5. existing artifacts: manifest JSON, skill docs, previous release payloads
6. live integration list results after OAuth, when local code does not already identify the update target
7. live external app list results after OAuth, when OAuth is required

Prefer targeted searches such as `rg "tool_name|registerTool|FastMCP|Authorization|Bearer|app_id|scope|endpoint"` over broad file dumps.

Categorize findings as:

- confirmed: directly present in code or config
- inferred: likely correct but not explicit
- missing: must be supplied by the user

Never silently invent `mcp.endpoint`, the release MCP endpoint, `oauth.appId`, tool mappings, or secrets.

#### MCP Suitability Analysis

If no existing MCP server is detected, scan for public functions, API routes, or logic blocks that would be valuable as AI tools. Suggest a small candidate tool list to the user.

Do not stop at "this project has no MCP." Continue by proposing the MCP-facing shape the project should adopt:

- recommend the smallest useful tool set, usually 2-5 tools
- for each candidate tool, specify:
    - proposed `toolName`
    - user-facing purpose
    - input shape
    - output shape
    - auth requirement
    - backing code path or route
- recommend whether the project should expose:
    - an HTTP MCP endpoint in the existing app, or
    - a small dedicated MCP server that calls the existing app over HTTP
- prefer `authMode = bearer_token` for user-scoped integrations that need a runtime bearer token
- keep `actions[].toolName` and `mcp.toolAllow` identical to the real MCP tool names

After the user approves the direction, continue with the appropriate planning or implementation work so those candidate capabilities are exposed as a real MCP server in the project's codebase before returning to the integration payload and save flow.

#### MCP Runtime Auth And User Resolution

When SecondMe invokes an MCP endpoint for a user-scoped integration, it passes the current user's access token through the `Authorization` header.

Treat this token as the runtime user context for the MCP request, not as a static app credential.

Implementation rules for MCP services:

- read `Authorization: Bearer <accessToken>` from the incoming MCP request
- reject missing or malformed bearer tokens immediately
- use that access token to call the upstream user info endpoint, or an equivalent identity endpoint, to identify the current SecondMe user
- map that upstream user identity to the app's local user model, typically through `oauth_id` or an equivalent stable external id
- if the local user does not exist yet, upsert it before running the business logic
- execute MCP-backed business logic with the resolved local user id, not with an anonymous or global app context
- return `401` for missing or invalid tokens, `403` for resources not owned by the resolved user, and `404` only for truly missing resources

Architecture guidance based on `SemeCompat`:

- prefer keeping token parsing and local-user resolution in the app's own HTTP API layer
- let the standalone MCP server or transport layer forward the bearer token, but not own user persistence
- keep MCP tools thin: they should call app routes that already enforce bearer auth and user ownership
- if the MCP server calls internal app APIs over HTTP, forward the same `Authorization` header unchanged

### 2. Draft The Integration Payload

Build a candidate payload with:

- `manifest.skill`
- `manifest.prompts`
- `manifest.actions`
- `manifest.mcp`
- `manifest.oauth` when user-level auth is required
- `manifest.envBindings.release`
- `envSecrets.release.values` for actual placeholders only

Inference rules:

- Key: prefer an existing integration key; otherwise derive from the repo name in kebab-case
- Display name and description: derive from README or package metadata
- Prompts: infer from usage examples, prompt files, skill docs, or README; if signal is low, draft conservative prompts and mark them inferred
- Actions: map directly to real MCP tools; keep `toolName` identical to the registration
- MCP auth: if the MCP requires `Authorization: Bearer {{token}}`, set `authMode` to `bearer_token`
- for `bearer_token`, assume the runtime token represents the current SecondMe user and the service must resolve that user server-side
- If custom placeholder headers are required, set `authMode` to `header_template`
- If no auth is required, use `none`

Additional rules:

- `skill.key` is blocking; if two plausible keys exist, ask the user
- If the user explicitly asks for a new key, such as `foo-v2`, treat that as a new integration candidate and do not auto-convert it into an update of the old key
- Do not finalize `oauth.appId` from code discovery alone
- Never infer a release MCP endpoint from local code alone; it must be user-confirmed
- `envSecrets.release.values` must only contain placeholders actually needed by templates or deployment config
- If `authMode` is `bearer_token`, do not default to a manual `Authorization` header template; prefer leaving `headersTemplate` empty unless a real custom header template is required
- for user-scoped tools, do not design the MCP service around a shared service account; the request must run as the user identified by the runtime access token

For OAuth:

- After CLI OAuth succeeds, query the external app list and rank likely `oauth.appId` candidates from the project name and `skill.key`
- If one candidate is clearly best, present it to the user for confirmation
- If multiple candidates are close, show a short ranked list and ask the user to choose
- If no candidate is plausible, ask the user to provide `oauth.appId` manually

Before deciding whether this is `create` or `update`:

- If the repo already contains an integration id, treat it as an update candidate
- Otherwise use the integration list API to look for an existing integration owned by the same user
- Compare by stable fields such as `skill.key` and confirmed project identity
- If exactly one strong match exists, treat it as an update candidate
- If there is no match, prepare a create payload
- If there are multiple plausible matches, stop and ask which integration to update
- If the user explicitly asked for a new integration key, only use the list to detect exact key collisions and avoid duplicates; do not silently overwrite a different integration

### 3. Confirm Blocking Fields Before Any Write

Before calling create, update, or release, show a compact summary and explicitly confirm:

- `skill.key`
- `skill.displayName`
- `skill.description`
- `prompts.activationShort`
- `prompts.activationLong`
- `prompts.systemSummary`
- `mcp.endpoint`
- the online release endpoint
- `oauth.appId` if applicable
- the matched existing integration, if one was found
- operation type: `create` or `update`
- immediate release choice

Stop and ask if:

- the endpoint is localhost or still inferred
- the online MCP endpoint is missing
- the prompts are still inferred and have not been shown to the user
- actions or tool mapping are ambiguous
- the matched integration is not explicitly confirmed
- required secrets are missing
- release binding is incomplete

Do not release without explicit user confirmation in the current conversation.

### 4. Run CLI OAuth

Use the gateway API base:

- `https://app.mindos.com/gate/lab/api`

Do not assume `https://develop.second.me/api` is a working API base.

Process:

1. Create a CLI auth session
2. Show the user:
    - the auth URL: `https://develop.second.me/auth/cli?session={sessionId}`
    - the `userCode`
3. Tell the user that if the page asks for a code manually, they should paste `userCode`
4. Poll until authorized or expired
5. Validate which token form actually works in the current environment
6. Fetch the external app list to rank and confirm `oauth.appId`

CLI auth endpoints:

- `POST /auth/cli/session`
- `GET /auth/cli/session/{sessionId}/poll`
- optional:
    - `POST /auth/cli/session/{sessionId}/authorize`
    - `POST /auth/cli/session/authorize-by-code`

Path rule:

- These routes are relative to the gateway base `https://app.mindos.com/gate/lab/api`
- Do not prepend an extra `/api`
- If these routes return `404`, first check whether you accidentally called `.../gate/lab/api/api/...`

Expected session response shape:

```json
{
  "code": 0,
  "data": {
    "sessionId": "uuid",
    "userCode": "ABCD-1234",
    "expiresAt": "2026-03-18T12:00:00Z"
  }
}
```

Poll outcomes:

- `pending`: keep polling until expiry
- `authorized`: extract the token from `data.token`
- `expired`: stop and ask whether to create a new session

Token validation rule:

- Start with the token exactly as returned by CLI auth
- First try `Authorization: Bearer <token>`
- If the token contains `|suffix` and the full token returns `401`, retry once with the substring before `|`
- Use the first working form for the rest of the session
- Do not ask the user whether to strip the suffix; validate it directly
- Surface which form worked if it materially affects follow-up debugging

Integration and external app routes:

- `GET /applications/external/list?page=1&page_size=20`
- `GET /integrations/list?page=1&pageSize=20`
- `GET /integrations/{integrationId}`
- `POST /integrations/create`
- `POST /integrations/{integrationId}/update`
- `POST /integrations/{integrationId}/release`

Route debugging rule:

- If integration or external app routes return `404`, verify that you are calling `https://app.mindos.com/gate/lab/api/...` and not `https://app.mindos.com/gate/lab/api/api/...`
- Do not conclude that the backend is missing the feature until the duplicated-path possibility has been ruled out

If the environment does not expose the CLI auth endpoints, stop and tell the user the backend branch or deployment is missing the required OAuth support.

### 5. Save The Integration

- Update: if an existing integration id is confirmed
- Create: if no matching integration is found after list lookup

After save:

- surface the `integrationId`
- report the saved version
- fetch integration detail if needed to verify the saved state
- do not print raw secret values in the summary
- if the user only asked to save or create, stop after reporting the saved state instead of continuing into release automatically

### 6. Release The Integration

Only release if the user explicitly requests it after a successful save.

Before release, verify:

- the integration save succeeded
- the release binding is enabled
- the endpoint came explicitly from the user
- the endpoint is not local-only unless the user explicitly wants local testing
- for `bearer_token` integrations, `headersTemplate` does not manually render `Authorization: Bearer {{token}}` unless the release environment truly provides a matching secret placeholder

If release fails:

1. Fetch the integration detail immediately
2. Inspect the latest version's `validationReport`
3. Report the exact failing environment, error text, and whether tool discovery succeeded
4. Fix the manifest or env secret cause before retrying

Common release failure pattern:

- If `authMode = bearer_token` and `headersTemplate.Authorization = "Bearer {{token}}"`, release validation may fail with an empty rendered header such as `Bearer `
- In that case, prefer an empty `headersTemplate` and let bearer-token handling inject auth automatically
- Only use `headersTemplate` or `envSecrets.release.values.token` when a real custom placeholder-based header is required

Implementation checklist before save or release:

- the MCP endpoint accepts `Authorization: Bearer <accessToken>`
- the app resolves the upstream SecondMe user from that token
- the app maps or upserts that user into the local user table before business logic runs
- protected resources are checked against the resolved local user
- the standalone MCP server forwards the incoming bearer token unchanged when calling internal app APIs
- tests cover missing token, invalid token, existing-user resolution, new-user upsert, bearer-token forwarding, and resource-ownership failures

Release request body:

```json
{}
```

Or for a specific version:

```json
{
  "versionId": "ver_xxx"
}
```

Report the resulting state precisely, such as `pending_review`, instead of loosely saying it is live.

## Payload Schema

```json
{
  "manifest": {
    "schemaVersion": "1",
    "skill": {
      "key": "example-skill",
      "displayName": "Example Skill",
      "description": "What the skill does",
      "keywords": ["example"]
    },
    "prompts": {
      "activationShort": "...",
      "activationLong": "...",
      "systemSummary": "..."
    },
    "actions": [
      {
        "name": "toolAlias",
        "description": "What the action does",
        "toolName": "real_mcp_tool_name",
        "payloadTemplate": {},
        "displayHint": "text"
      }
    ],
    "mcp": {
      "endpoint": "https://api.example.com/mcp",
      "timeoutMs": 12000,
      "toolAllow": ["real_mcp_tool_name"],
      "headersTemplate": {},
      "authMode": "bearer_token"
    },
    "oauth": {
      "appId": "app_xxx",
      "requiredScopes": ["profile:read"]
    },
    "envBindings": {
      "release": {
        "enabled": true,
        "endpoint": "https://api.example.com/mcp"
      }
    }
  },
  "envSecrets": {
    "release": null
  }
}
```

Field notes:

- `schemaVersion` is currently `"1"`
- `toolName` must be the exact MCP tool name
- `headersTemplate` supports placeholders such as `{{token}}`, but do not use it by default for `bearer_token`
- `authMode` is one of `none`, `bearer_token`, or `header_template`
- `oauth.appId` must be user-confirmed before save or release
- `envBindings.release.endpoint` should use the user-provided online MCP endpoint
- `envSecrets` should only contain values actually needed to render release-time placeholders

## Response Style

- Compact: use tables or bullet lists for summaries
- Transparent: clearly distinguish between confirmed and inferred data
- Precise: use exact API error messages if a step fails
- Security-first: never repeat secret values back to the user

## Operational Rules

- Always list integrations before assuming `create` is needed
- Always list external apps before asking for manual `appId` entry
- Ensure the user provides the production MCP endpoint before any release attempt
- If create or update fails, surface the API error and the manifest section most likely responsible
- If release fails, return the exact review or validation state instead of summarizing loosely
- If release fails, inspect `validationReport` before changing anything
- When the project has no MCP server yet, do not stop at suitability analysis; provide a concrete MCP exposure recommendation and hand off to planning or implementation after user approval
