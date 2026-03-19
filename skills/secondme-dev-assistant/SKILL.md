---
name: secondme-dev-assistant
description: Use when the user wants to create a SecondMe app, obtain Client ID or Client Secret, define requirements, scaffold or plan a SecondMe project, implement SecondMe OAuth or MCP integration rules, or manage app and integration records on SecondMe Develop.
---

# SecondMe Dev Assistant

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

## Phase 1: Create The SecondMe App And Obtain Credentials

When the user needs a SecondMe app, default to creating it for them through the platform APIs after collecting the required fields and completing authentication.

Required outcome:

- app exists on the platform
- user has `Client ID`
- user has `Client Secret`
- user knows the redirect URIs and allowed scopes

### Bootstrap Decision

First determine which of these is true:

- user already has complete `App Info`
- user has partial credentials
- user has no app yet

If the user has no app yet:

1. collect the minimum fields needed to create the app
2. authenticate to SecondMe Develop
3. create the app on the user's behalf through the external app create API
4. capture the returned `Client ID` and `Client Secret`
5. save the secret to `~/.secondme/client_secret`
6. explicitly tell the user that the app was created and the secret has already been saved

Only tell the user to go to [develop.second.me](https://develop.second.me) and create it manually when:

- the user explicitly says they want to do it themselves
- required information is still missing and they do not want the assistant to make reasonable defaults
- current auth or platform access prevents the assistant from creating the app directly

### Preferred Input: App Info

Prefer parsing this format:

```text
## App Info
- App Name: my-app
- Client ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
- Client Secret: your-secret-here
- Redirect URIs:
  - http://localhost:3000/api/auth/callback
  - https://my-app.vercel.app/api/auth/callback
- Allowed Scopes: user.info, user.info.shades, chat, note.add
```

Extract:

- `appName`
- `clientId`
- `clientSecret`
- `redirectUris`
- `allowedScopes`

If both local and production callback URLs are present, prefer the local development callback as the default working callback and keep the full list for future configuration.

### Manual Input Fallback

If App Info is unavailable, collect:

- `App Name`
- `App Description` when available
- `Redirect URIs`
- `Allowed Scopes`

Then create the app on the user's behalf unless they explicitly want to operate manually.

### Scope-To-Module Inference

Infer the likely app capabilities from scopes:

| Scope | Module |
|------|------|
| `user.info` | `auth` |
| `user.info.shades` | `profile` |
| `user.info.softmemory` | `profile` |
| `chat` | `chat` |
| `chat` | `act` |
| `note.add` | `note` |
| `voice` | `voice` reference only |

Treat `auth` as mandatory whenever `user.info` is present, which is the normal case.

## Phase 2: Client Secret Handling

Some actions require the OAuth app `Client Secret`.

Secret file:

- path: `~/.secondme/client_secret`
- directory: `~/.secondme`
- preferred permissions: directory `700`, file `600`

Rules:

1. if the task needs `clientSecret`, first try reading `~/.secondme/client_secret`
2. if the file is missing or empty, ask the user for the secret and save it there
3. after saving, continue using the stored value instead of re-asking
4. never print the raw secret in summaries
5. never invent or silently keep a placeholder

Creation and regeneration rules:

- if this assistant creates an external app and the API returns a new `clientSecret`, save it immediately to `~/.secondme/client_secret`
- if this assistant regenerates the secret and the API returns a new `clientSecret`, replace the file immediately
- after either action, explicitly tell the user that the secret was obtained and already saved to `~/.secondme/client_secret`
- if regeneration happens, also remind the user that the old secret is now invalid

Conflict rule:

- if a different secret already exists and the current task is clearly for another app, warn before overwriting
- if the current flow just created or regenerated the secret for the app being configured, overwrite it and explain what changed

Failure recovery:

- if an API call fails with invalid client, invalid secret, unauthorized client, or another secret-related auth error, treat the stored secret as stale or incorrect
- tell the user the secret in `~/.secondme/client_secret` may be invalid or expired and ask them to replace it
- do not silently keep retrying with the same value

## Phase 3: Clarify Requirements And Produce A Scaffold Plan

When the user wants to build a SecondMe app, do requirement discovery before project generation.

Collect:

- product goal
- target users
- chosen modules
- key user flows
- preferred UI tone
- storage needs
- whether they want a quick start or a fuller requirements pass

### Standard Planning Mode

Use when the user wants a thoughtful project plan.

Clarify:

- what problem the app solves
- who uses it
- what the minimum useful feature set is
- which SecondMe capabilities are actually needed
- what local persistence is required
- what kind of review submission they eventually want

### Quick Start Mode

Use when the user wants a fast setup and accepts defaults.

Defaults:

- framework: Next.js with App Router
- language: TypeScript
- styling: Tailwind CSS
- ORM: Prisma
- local dev port: `3000`
- backend style: Next.js route handlers as proxy or app API layer

### Output Of This Phase

Do not jump straight into code generation. Produce a concrete build brief that the user's coding tool can execute.

The brief should include:

- app summary
- selected modules
- recommended stack
- required pages and API routes
- database tables
- environment variables
- OAuth flow steps
- MCP or integration requirements if relevant
- test checklist

### Optional Local Handoff Artifacts

If the user wants the planning state captured in the repo, it is acceptable to maintain:

- `.secondme/state.json`
- `CLAUDE.md`

Suggested state structure:

```json
{
  "version": "1.0",
  "appName": "my-app",
  "modules": ["auth", "chat", "profile"],
  "config": {
    "clientId": "xxx",
    "redirectUris": ["http://localhost:3000/api/auth/callback"],
    "allowedScopes": ["user.info", "chat"]
  },
  "api": {
    "baseUrl": "https://api.mindverse.com/gate/lab",
    "oauthUrl": "https://go.second.me/oauth/",
    "tokenEndpoint": "https://api.mindverse.com/gate/lab/api/oauth/token/code",
    "refreshEndpoint": "https://api.mindverse.com/gate/lab/api/oauth/token/refresh"
  },
  "docs": {
    "quickstart": "https://develop-docs.second.me/zh/docs",
    "oauth2": "https://develop-docs.second.me/zh/docs/authentication/oauth2",
    "apiReference": "https://develop-docs.second.me/zh/docs/api-reference/secondme",
    "errors": "https://develop-docs.second.me/zh/docs/errors"
  },
  "prd": {
    "summary": "",
    "features": [],
    "targetUsers": "",
    "designPreference": ""
  }
}
```

## Phase 4: Implementation Guidance And SecondMe Standards

This phase tells the user or their coding tool how to build the app correctly.

### Recommended Project Shape

Default recommendation for web apps:

- Next.js App Router
- TypeScript
- Tailwind CSS
- Prisma
- local port `3000`

Suggested responsibilities:

- app UI layer
- local auth/session layer
- proxy or server API routes for upstream SecondMe APIs
- persistence for user tokens and app data
- MCP-facing or integration-facing API layer if needed

### Required Environment Variables

```env
SECONDME_CLIENT_ID=...
SECONDME_CLIENT_SECRET=...
SECONDME_REDIRECT_URI=...
SECONDME_API_BASE_URL=https://api.mindverse.com/gate/lab
SECONDME_OAUTH_URL=https://go.second.me/oauth/
SECONDME_TOKEN_ENDPOINT=https://api.mindverse.com/gate/lab/api/oauth/token/code
SECONDME_REFRESH_ENDPOINT=https://api.mindverse.com/gate/lab/api/oauth/token/refresh
DATABASE_URL=...
```

### OAuth2 Rules

Base URL:

- `https://api.mindverse.com/gate/lab`

OAuth URL:

- `https://go.second.me/oauth/`

Important OAuth rule:

- `oauthUrl` already contains the full path
- append `?` and query parameters directly
- do not append `/authorize`

Example:

```typescript
const authUrl = `${process.env.SECONDME_OAUTH_URL}?${params.toString()}`;
```

### Token Exchange

Endpoint:

- `POST {baseUrl}/api/oauth/token/code`

Request type:

- `application/x-www-form-urlencoded`

Do not send JSON.

Response shape:

```json
{
  "code": 0,
  "data": {
    "accessToken": "lba_at_xxx",
    "refreshToken": "lba_rt_xxx",
    "tokenType": "Bearer",
    "expiresIn": 7200,
    "scope": ["user.info", "chat"]
  }
}
```

Rules:

- always check `result.code`
- actual payload is under `result.data`
- fields use camelCase

### Token Refresh

Endpoint:

- `POST {baseUrl}/api/oauth/token/refresh`

Request type:

- `application/x-www-form-urlencoded`

### Recommended User Table Fields

Any implementation that persists user auth should retain at least:

- local `id`
- stable upstream user id such as `secondmeUserId` or `oauthId`
- `accessToken`
- `refreshToken`
- `tokenExpiresAt`
- timestamps

### WebView OAuth Note

In WebView-like environments, strict OAuth state verification may fail because storage is not shared across browser contexts.

If the product is explicitly targeting a trusted WebView environment, it is acceptable to warn and continue rather than hard-failing on state mismatch. Call out the CSRF tradeoff clearly.

### API Response Handling

All SecondMe API responses should be treated as:

```json
{
  "code": 0,
  "data": {}
}
```

Do not consume the raw top-level JSON as if it were the actual array or object.

### Optional Capability References

Use when relevant:

- `chat`: normal conversational output
- `act`: structured JSON decision output over streaming
- `note.add`: note or memory creation
- `agent_memory/ingest`: reporting external user actions into Agent Memory

## Phase 5: MCP And Integration Implementation Guidance

When the user needs MCP or SecondMe integration support, guide them toward the smallest valid MCP surface.

If the user asks how to use their own app through OpenClaw, guide them through the real platform path instead of answering abstractly.

Use this explanation:

1. the app capability must be exposed through an MCP server or MCP-compatible endpoint
2. that MCP capability must be submitted to SecondMe as an integration
3. the integration must pass review
4. once approved, the app's integration can be discovered through the official skill third-party app list on the SecondMe platform
5. after it becomes discoverable there, OpenClaw can use the integration and call the app's exposed functionality

Routing rules for this request shape:

- if the user asks how OpenClaw can use their app, first confirm whether they already have an MCP server
- if they do not have one yet, guide them to design and build the MCP server first
- if they already have one, continue with integration create, validate, and release guidance
- if they only have a normal OAuth app and no MCP surface, explain that app creation alone is not enough for OpenClaw tool usage and that an MCP-facing integration is still required

### Repository Scan Rules

Only read the files needed to infer the integration or MCP suitability.

Search order:

1. `README*`, `package.json`, `pyproject.toml`, `Cargo.toml`
2. `mcp.json`, `*.mcp.*`, server configs, deployment manifests
3. tool registration or router code
4. auth and env files
5. existing manifests or skill docs
6. live integration list after auth if local code is insufficient
7. live app list after auth if OAuth binding is needed

Prefer targeted searches such as:

- `rg "tool_name|registerTool|FastMCP|Authorization|Bearer|app_id|scope|endpoint"`

Categorize findings as:

- `confirmed`
- `inferred`
- `missing`

Never invent:

- `mcp.endpoint`
- release endpoint
- `oauth.appId`
- tool mappings
- secrets

### MCP Suitability Guidance

If no MCP server exists yet, do not stop there.

Propose:

- the minimum useful tool set, usually `2-5` tools
- the actual tool names
- user-facing purpose
- input shape
- output shape
- auth requirement
- backing route or code path

Recommend one of:

- an HTTP MCP endpoint inside the existing app
- a thin MCP server that calls the existing app over HTTP

### MCP Runtime Auth Rules

For user-scoped integrations, prefer:

- `authMode = bearer_token`

Runtime behavior:

- read `Authorization: Bearer <accessToken>`
- reject malformed or missing tokens
- resolve the upstream SecondMe user from the token
- map or upsert the local user
- run business logic using the resolved local user id
- return `401`, `403`, or `404` appropriately

Architecture guidance:

- token parsing and user resolution should live in the app API layer
- MCP transport should stay thin
- if MCP calls internal APIs, forward `Authorization` unchanged

### Recommended Tests

- missing bearer token rejects the request
- invalid bearer token maps to `401`
- existing upstream user resolves correctly
- new upstream user is upserted correctly
- MCP-to-app forwarding preserves `Authorization`
- ownership violations return `403`

## Phase 6: Authenticate With SecondMe Develop CLI Auth

Use the gateway base:

- `https://app.mindos.com/gate/lab/api`

Routes:

- `POST /auth/cli/session`
- `GET /auth/cli/session/{sessionId}/poll`
- `POST /auth/cli/session/{sessionId}/authorize`
- `POST /auth/cli/session/authorize-by-code`

Process:

1. create a CLI auth session
2. show the user:
   - auth URL: `https://develop.second.me/auth/cli?session={sessionId}`
   - `userCode`
   - expiry time if available
3. tell the user that if the page asks for a manual code, they should paste `userCode`
4. poll until `authorized`, `expired`, or timeout
5. if the token contains `|suffix`, strip the suffix and use only the substring before `|`
6. if the token does not contain `|suffix`, use it as returned
7. use that normalized token form for the rest of the session

Poll states:

- `pending`
- `authorized`
- `expired`

Route debugging rule:

- if you see `404`, first verify you are calling `https://app.mindos.com/gate/lab/api/...`
- do not prepend another `/api`

## Phase 7: Manage External OAuth Apps On SecondMe Develop

Treat external apps as first-class control-plane objects.

Developer routes:

- `GET /applications/external/list`
- `GET /applications/external/{appId}`
- `POST /applications/external/create`
- `POST /applications/external/{appId}/update`
- `POST /applications/external/{appId}/regenerate-secret`
- `POST /applications/external/{appId}/delete`
- `POST /applications/external/{appId}/apply-listing`

Public routes:

- `GET /applications/external/public/list`
- `GET /applications/external/{appId}/public`

Create request shape:

```json
{
  "appName": "Example App",
  "appDescription": "Optional description",
  "redirectUris": ["https://example.com/oauth/callback"],
  "allowedScopes": ["user.info"]
}
```

Update request shape:

```json
{
  "appName": "Example App",
  "appDescription": "Optional description",
  "redirectUris": ["https://example.com/oauth/callback"],
  "allowedScopes": ["user.info", "chat"]
}
```

External app rules:

- default to operating on behalf of the user once auth is available
- always list apps before deciding a new app must be created
- if one app is an obvious match, present it for confirmation
- if multiple apps are plausible, show a short ranked list and ask the user to choose
- if no app exists yet, collect the required creation fields and create it directly instead of telling the user to do it manually
- only switch to self-serve instructions when the user explicitly wants to operate manually or the assistant is blocked by missing permissions or missing required inputs
- `clientSecret` is returned only on create or regenerate, so capture it immediately
- `GET /applications/external/{appId}` does not return the raw secret

### Listing Media URL Handling

Some app listing fields require a usable asset URL rather than a local file path.

Typical fields:

- `iconUrl`
- `ogImageUrl`
- `screenshots`
- `promoVideoUrl`

Handling rule:

1. ask the user whether they already have an existing public URL for each needed asset
2. if they provide an existing URL, use it directly
3. if they provide a local file instead, upload it through the CDN upload API first
4. write the returned CDN URL into the listing payload

CDN upload API:

- `POST /api/cdn/upload`

Upload request rules:

- send `multipart/form-data`
- form field name: `file`
- include the authenticated platform token in the `token` header
- do not send JSON for this upload

Expected upload response shape:

```json
{
  "code": 0,
  "data": {
    "url": "https://cdn.example.com/path/to/file.png",
    "key": "path/to/file.png"
  }
}
```

Use `result.data.url` as the value written into:

- `iconUrl`
- `ogImageUrl`
- each item in `screenshots`
- `promoVideoUrl` when the user provides a local promo video file instead of a remote URL

If the user provides neither a URL nor a local file:

- leave the field empty unless it is required for the quality bar they want
- if the field is optional, explain the review tradeoff and let the user decide whether to continue

### Apply-Listing Review Guidance

When preparing `apply-listing`, do not treat optional review fields as irrelevant.

These are not strictly required, but leaving them empty may reduce review approval rate:

- `subtitle`
- `iconUrl`
- `ogImageUrl`
- `screenshots`
- `promoVideoUrl`
- `websiteUrl`
- `supportUrl`
- `privacyPolicyUrl`

If some are empty:

- explicitly recommend that the user fill them in before submission
- if the user confirms they do not want to provide them, allow the submission to proceed
- if screenshots or media assets are missing, say this is allowed but may weaken review quality

## Phase 8: Manage Integrations On SecondMe Develop

Developer routes:

- `GET /integrations/list?page=1&pageSize=20`
- `GET /integrations/{integrationId}`
- `POST /integrations/create`
- `POST /integrations/{integrationId}/update`
- `POST /integrations/{integrationId}/delete`
- `POST /integrations/{integrationId}/validate`
- `POST /integrations/{integrationId}/release`

Use these actions to cover the Develop list and detail pages:

- query list
- inspect detail
- edit manifest
- save draft
- delete integration
- validate latest or specific version
- submit release review

Manifest shape:

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
      "requiredScopes": ["user.info"]
    },
    "envBindings": {
      "release": {
        "enabled": true,
        "endpoint": "https://api.example.com/mcp"
      }
    }
  },
  "envSecrets": {
    "release": {
      "values": {}
    }
  }
}
```

Field rules:

- `skill.key` is blocking and must be stable
- if the user explicitly asks for a new key, treat it as a new integration candidate
- `toolName` must match the actual MCP tool name exactly
- `authMode` must be one of `none`, `bearer_token`, or `header_template`
- `oauth.appId` must be user-confirmed
- `envBindings.release.endpoint` must be user-confirmed
- `envSecrets.release.values` must contain only values actually required by endpoint or header templates

Create vs update rules:

- if the user or repo already identifies an integration id, treat it as an update candidate
- otherwise list integrations and match by `skill.key` plus confirmed project identity
- if exactly one strong match exists, present it as the update target
- if there is no match, prepare a create payload
- if there are multiple plausible matches, ask the user which one to update

## Phase 9: Validate, Release, And Review Maintenance

Rules:

- validate before suggesting release
- only release if the user explicitly requests it after save succeeds
- confirm the target integration and version before release
- confirm the release endpoint before release
- do not release if the endpoint is still local-only unless the user explicitly wants local testing
- for `bearer_token` integrations, prefer an empty `headersTemplate` unless a real custom header template is required

If release fails:

1. fetch integration detail immediately
2. inspect the latest version's `validationReport`
3. inspect whether `pendingReleaseReview` exists or `releaseStatus` is `pending_review`
4. if the integration is still in review, tell the user that the previous review is probably still pending and that a new submission is usually blocked until that review finishes
5. otherwise report the exact failing environment and error text
6. fix the manifest or secret cause before retrying

Common failure pattern:

- if `authMode = bearer_token` and `headersTemplate.Authorization = "Bearer {{token}}"`, release validation may fail with an empty rendered header
- in that case, prefer leaving `headersTemplate` empty and letting bearer-token handling inject auth automatically

If release succeeds and the later review passes:

- explain that the integration should become discoverable through the official skill third-party app list on the SecondMe platform
- explain that OpenClaw can then use that integration to access the app's exposed MCP tools
- if the user's goal is OpenClaw usage, explicitly say that integration approval is the milestone that enables that path

## Confirmation Rules Before Any Write

Before create, update, delete, regenerate-secret, apply-listing, validate, or release, summarize the exact target and action.

Before integration create or update, explicitly confirm:

- `skill.key`
- `skill.displayName`
- `skill.description`
- `prompts.activationShort`
- `prompts.activationLong`
- `prompts.systemSummary`
- `mcp.endpoint`
- release endpoint
- `oauth.appId` if applicable
- matched integration if any
- operation type: `create` or `update`

Before external app create or update, explicitly confirm:

- `appName`
- `appDescription`
- `redirectUris`
- `allowedScopes`
- matched app if any
- operation type: `create` or `update`

Before destructive or secret-changing actions, explicitly confirm:

- integration delete
- external app delete
- regenerate secret
- release submission

Stop and ask if:

- the endpoint is localhost or still inferred
- `oauth.appId` is still inferred
- prompts were inferred but not shown
- action or tool mapping is ambiguous
- required secrets are missing
- the app or integration match is ambiguous

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
