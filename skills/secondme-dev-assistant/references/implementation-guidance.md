# Implementation Guidance & SecondMe Standards (Phase 4)

## Contents

- [Recommended Project Shape](#recommended-project-shape)
- [Required Environment Variables](#required-environment-variables)
- [OAuth2 Rules](#oauth2-rules)
- [Token Exchange](#token-exchange)
- [Token Refresh](#token-refresh)
- [Recommended User Table Fields](#recommended-user-table-fields)
- [WebView OAuth Note](#webview-oauth-note)
- [API Response Handling](#api-response-handling)
- [API Endpoint Discovery Rule](#api-endpoint-discovery-rule)
- [Optional Capability References](#optional-capability-references)

This phase tells the user or their coding tool how to build the app correctly.

## Recommended Project Shape

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

## Required Environment Variables

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

## OAuth2 Rules

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

## Token Exchange

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

## Token Refresh

Endpoint:

- `POST {baseUrl}/api/oauth/token/refresh`

Request type:

- `application/x-www-form-urlencoded`

## Recommended User Table Fields

Any implementation that persists user auth should retain at least:

- local `id`
- stable upstream user id such as `secondmeUserId` or `oauthId`
- `accessToken`
- `refreshToken`
- `tokenExpiresAt`
- timestamps

## WebView OAuth Note

In WebView-like environments, strict OAuth state verification may fail because storage is not shared across browser contexts.

If the product is explicitly targeting a trusted WebView environment, it is acceptable to warn and continue rather than hard-failing on state mismatch. Call out the CSRF tradeoff clearly.

## API Response Handling

All SecondMe API responses should be treated as:

```json
{
  "code": 0,
  "data": {}
}
```

Do not consume the raw top-level JSON as if it were the actual array or object.

## API Endpoint Discovery Rule

Do not guess or infer API paths from scope names. API paths do not follow an obvious naming convention (e.g. `user.info` scope does not map to `/api/user/info` — the actual path is `/api/secondme/user/info`).

Remote source of truth:

- `https://develop-docs.second.me/zh/docs/api-reference/secondme`

Local cache:

- path: `references/api-reference.md` (relative to this skill's base directory)
- this file is NOT distributed with the skill — it is created and maintained locally by the agent

Bootstrap rule (first use):

1. Before writing any code that calls SecondMe data APIs, check if `references/api-reference.md` exists
2. If it does not exist, create the `references/` directory and fetch the remote docs
3. Extract all endpoint paths, methods, request/response shapes, and required scopes
4. Save to `references/api-reference.md` with a `fetched_at` field in the frontmatter set to today's date
5. Then use the local file for implementation

Subsequent use rule:

1. Read `references/api-reference.md` to get endpoint paths, parameters, and response shapes
2. Use only the paths from that reference — never invent or infer paths

Freshness check rule:

- If `fetched_at` in the reference file is older than 7 days, fetch the remote docs before writing code
- After fetching, compare with the local reference
- If there are differences (new endpoints, changed paths, changed parameters), update the local reference file and set `fetched_at` to today
- If no differences, only update `fetched_at` to today
- If the remote fetch fails (network error, 404, etc.), fall back to the local reference but warn the user that it may be stale

## Optional Capability References

Use when relevant:

- `chat`: normal conversational output
- `act`: structured JSON decision output over streaming
- `note.add`: note or memory creation
- `agent_memory/ingest`: reporting external user actions into Agent Memory
