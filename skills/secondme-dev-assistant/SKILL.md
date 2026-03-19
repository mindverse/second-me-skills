---
name: secondme-dev-assistant
description: Use when the user wants to create, query, edit, save, validate, release, or delete SecondMe Develop integrations or external OAuth apps, or needs to derive those changes from a local project.
---

# SecondMe Dev Assistant

This skill is a full SecondMe Develop control-plane assistant. It can:

- infer integration payloads from a local project
- manage `Integrations` records end to end
- manage `External OAuth Apps` end to end
- run CLI auth for developer APIs
- handle `Client Secret` capture, local persistence, and failure recovery

Do not treat this skill as a manifest form filler only. If the user wants something they can do on [SecondMe Develop](https://develop.second.me/integrations/list), assume this skill should help complete it unless the task is clearly outside integrations or external apps.

## Use This Skill For

- Creating or updating an integration from local code
- Querying existing integrations or external apps
- Editing and saving an existing integration or external app
- Validating an integration before release
- Submitting a release after explicit user confirmation
- Deleting an integration or external app
- Creating or updating the OAuth app bound by `manifest.oauth.appId`
- Regenerating, storing, or replacing `Client Secret`

Do not use this skill to guess secrets, invent missing endpoints, bypass confirmation for destructive actions, or release without explicit approval in the current conversation.

## Invocation Defaults

- Display name: `SecondMe Builder Skill`
- Short description: `Manage SecondMe Develop integrations and OAuth apps from local code or existing records`
- Default prompt: `Use $secondme-dev-assistant to inspect this project or existing SecondMe records, manage the matching integration and OAuth app, save the result, and only release if I explicitly ask.`
- Implicit invocation: Allowed

## Operating Modes

Choose the smallest mode that matches the user request.

### 1. Project-Derived Mode

Use when the user wants to build or update an integration from a local repository.

- scan the project
- infer MCP and manifest fields
- identify whether an external OAuth app is needed
- create or update the app if needed
- create or update the integration
- validate
- optionally release only after explicit confirmation

### 2. Control-Plane Mode

Use when the user wants to work directly against existing records on SecondMe Develop.

- list, inspect, edit, save, validate, release, or delete integrations
- list, inspect, create, edit, save, regenerate secret, or delete external OAuth apps

If the user is only asking for control-plane data, do not force a repository scan first.

## Workflow

### 1. Identify The Target Domain

Classify the request before taking action:

- `integration`: `Integrations` list, detail, edit, save, validate, release, delete
- `external_app`: `OAuth2 Credentials`, app edit, create app, update app, regenerate secret, apply listing, delete app
- `project_to_integration`: derive integration fields from local code, then save them
- `mixed`: the user needs both an OAuth app and an integration bound together

If the request is mixed, prefer this order:

1. authenticate
2. inspect project if needed
3. resolve or create external app
4. resolve or create integration
5. validate
6. release only if explicitly requested

### 2. Authenticate With CLI Auth

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

- `pending`: keep polling
- `authorized`: use `data.token`
- `expired`: stop and ask whether to create a new session

Route debugging rule:

- if you see `404`, first verify you are calling `https://app.mindos.com/gate/lab/api/...`
- do not prepend another `/api`
- do not conclude the backend is missing the route until the duplicated-path mistake is ruled out

### 3. Handle Client Secret Correctly

Some operations need an OAuth app `Client Secret`. When that is needed, use this rule set.

Secret file:

- path: `~/.secondme/client_secret`
- directory: `~/.secondme`
- preferred file permissions: directory `700`, file `600`

Read/write rules:

1. if the task needs `clientSecret`, first try reading `~/.secondme/client_secret`
2. if the file is missing or empty, ask the user for the secret and save it there
3. after saving, continue using the file value instead of re-asking during the same and future turns
4. never print the raw secret back in summaries
5. never invent a placeholder and continue as if it were real

Creation and regeneration rules:

- if this assistant creates an external app and the API returns a new `clientSecret`, save it immediately to `~/.secondme/client_secret`
- if this assistant regenerates a secret and the API returns a new `clientSecret`, replace the file immediately
- after either action, explicitly tell the user that:
  - the `Client Secret` was obtained
  - it has already been saved to `~/.secondme/client_secret`
- when regeneration happens, also remind the user that the old secret is immediately invalid

Conflict rule:

- if a different secret is already present and the current task is clearly for another app, warn before overwriting
- if the current flow just created or regenerated the secret for the app being configured, overwrite the file and tell the user what changed

Failure recovery:

- if an API call fails with invalid client, invalid secret, unauthorized client, or another secret-related auth error, treat the local secret as stale or wrong
- tell the user the secret in `~/.secondme/client_secret` may be invalid or expired and ask them to replace it
- do not silently keep retrying with the same value

### 4. Project Scan Rules

Only use this section when local project context is relevant.

Read only the files needed to infer the integration or MCP suitability.

Search order:

1. metadata: `README*`, `package.json`, `pyproject.toml`, `Cargo.toml`
2. MCP config: `mcp.json`, `*.mcp.*`, server configs, deployment manifests
3. tool registration: entrypoints, decorators, router registrations, SDK setup
4. auth and env: `.env*`, example envs, secret templates, auth middleware
5. existing artifacts: manifest JSON, skill docs, previous payloads
6. integration list results after OAuth when local code does not already identify the target
7. external app list results after OAuth when OAuth is required

Prefer targeted searches such as:

- `rg "tool_name|registerTool|FastMCP|Authorization|Bearer|app_id|scope|endpoint"`

Categorize findings as:

- confirmed: directly present in code or config
- inferred: likely correct but not explicit
- missing: must be supplied by the user

Never silently invent:

- `mcp.endpoint`
- release endpoint
- `oauth.appId`
- tool mappings
- client secrets

### 5. MCP Suitability And Exposure Guidance

If no MCP server exists yet, do not stop at "no MCP found".

Propose the MCP-facing shape the project should adopt:

- recommend the smallest useful tool set, usually `2-5` tools
- for each candidate tool, specify:
  - `toolName`
  - user-facing purpose
  - input shape
  - output shape
  - auth requirement
  - backing code path or route
- recommend either:
  - an HTTP MCP endpoint inside the existing app, or
  - a thin MCP server that calls the existing app over HTTP

Auth guidance:

- prefer `authMode = bearer_token` for user-scoped integrations
- keep `actions[].toolName` and `mcp.toolAllow` identical to the real MCP tool names
- if the MCP server calls internal APIs, forward `Authorization` unchanged

### 6. Manage External OAuth Apps

Treat external apps as a first-class workflow, not as a side note under integrations.

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

Create request body:

```json
{
  "appName": "Example App",
  "appDescription": "Optional description",
  "redirectUris": ["https://example.com/oauth/callback"],
  "allowedScopes": ["user.info"]
}
```

Update request body:

```json
{
  "appName": "Example App",
  "appDescription": "Optional description",
  "redirectUris": ["https://example.com/oauth/callback"],
  "allowedScopes": ["user.info", "chat"]
}
```

Listing request body:

```json
{
  "slug": "example-app",
  "category": "tools",
  "tags": ["mcp", "developer"],
  "developerName": "Example Team"
}
```

External app rules:

- always list apps before deciding a new app must be created
- if one app is an obvious match for the project or integration, present it for confirmation
- if there are multiple plausible matches, show a short ranked list and ask the user to choose
- `clientSecret` is returned only on create or regenerate; capture it immediately
- `GET /applications/external/{appId}` does not return the raw secret
- if the user needs a secret later and it was not saved, ask for it or regenerate it explicitly

Apply-listing review guidance:

- when preparing `apply-listing`, do not treat optional review fields as irrelevant
- the following fields are not strictly required, but leaving them empty may reduce review approval rate:
  - `subtitle`
  - `iconUrl`
  - `ogImageUrl`
  - `screenshots`
  - `promoVideoUrl`
  - `websiteUrl`
  - `supportUrl`
  - `privacyPolicyUrl`
- if some of these fields are empty, explicitly recommend that the user fill them in before submission
- if the user confirms they do not want to provide them, allow the submission to proceed
- if screenshots or media assets are missing, say that this is allowed but may weaken review quality

### 7. Manage Integrations

Developer routes:

- `GET /integrations/list?page=1&pageSize=20`
- `GET /integrations/{integrationId}`
- `POST /integrations/create`
- `POST /integrations/{integrationId}/update`
- `POST /integrations/{integrationId}/delete`
- `POST /integrations/{integrationId}/validate`
- `POST /integrations/{integrationId}/release`

Use these actions to cover the SecondMe Develop list and edit pages:

- query list
- inspect detail
- edit manifest
- save draft
- delete integration
- validate latest or specific version
- submit release review

Manifest payload shape:

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
- `envBindings.release.endpoint` must be user-confirmed for online release
- `envSecrets.release.values` must contain only values actually required by endpoint or header templates

Create vs update rules:

- if the repo or user already identifies an existing integration id, treat it as an update candidate
- otherwise list integrations and match by `skill.key` plus confirmed project identity
- if exactly one strong match exists, present it as the update target
- if there is no match, prepare a create payload
- if there are multiple plausible matches, stop and ask which one to update

### 8. Runtime Auth And User Resolution For MCP

When `authMode = bearer_token`, treat the incoming bearer token as runtime user context.

Implementation rules:

- read `Authorization: Bearer <accessToken>` from the MCP request
- reject missing or malformed bearer tokens
- resolve the upstream SecondMe user from that token
- map or upsert the local user before business logic runs
- run business logic using the resolved local user id
- return:
  - `401` for missing or invalid token
  - `403` for ownership violations
  - `404` only for truly missing resources

Architecture guidance:

- prefer handling token parsing and local-user resolution inside the app API layer
- let the MCP transport stay thin
- if the MCP service calls internal APIs, forward the same `Authorization` header unchanged

### 9. Validate And Release

Validate route:

- `POST /integrations/{integrationId}/validate`

Release route:

- `POST /integrations/{integrationId}/release`

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

### 10. Confirm Blocking Fields Before Any Write

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
- matched integration, if any
- operation type: `create` or `update`

Before external app create or update, explicitly confirm:

- `appName`
- `appDescription`
- `redirectUris`
- `allowedScopes`
- matched app, if any
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

### 11. Response Style

- compact: use bullets or short tables for status summaries
- transparent: always distinguish `confirmed`, `inferred`, and `missing`
- precise: include exact API route or exact error message when useful
- security-first: never repeat raw secret values in summaries

### 12. Operational Rules

- always list records before assuming create is required
- always prefer the smallest necessary set of API calls
- if the user only asked to save or update, stop after reporting saved state
- if the user only asked to query, stop after reporting the requested data
- do not release automatically after save
- if this assistant created or regenerated a `Client Secret`, explicitly remind the user that it has already been saved to `~/.secondme/client_secret`
- if the saved secret later fails, tell the user to replace it rather than pretending the old one still works
