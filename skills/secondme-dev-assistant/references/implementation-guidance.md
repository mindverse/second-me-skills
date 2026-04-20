# Implementation Guidance & SecondMe Standards (Phase 4)

## Contents

- [Recommended Project Shape](#recommended-project-shape)
- [Required Environment Variables](#required-environment-variables)
- [OAuth2 Rules](#oauth2-rules)
- [Recommended User Table Fields](#recommended-user-table-fields)
- [Authorization Revocation Webhook](#authorization-revocation-webhook)
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
- webhook receiver route with raw-body signature verification if OAuth revocation handling is enabled
- MCP-facing or integration-facing API layer if needed

## Required Environment Variables

Fetch the OAuth2 doc page (https://develop-docs.second-me.cn/zh/docs/authentication/oauth2) to confirm the current base URL, OAuth URL, and token endpoints before populating these variables.

```env
SECONDME_CLIENT_ID=...
SECONDME_CLIENT_SECRET=...
SECONDME_REDIRECT_URI=...
SECONDME_API_BASE_URL=...          # from doc: base URL
SECONDME_OAUTH_URL=...             # from doc: authorization page URL
SECONDME_TOKEN_ENDPOINT=...        # from doc: token exchange endpoint
SECONDME_REFRESH_ENDPOINT=...      # from doc: token refresh endpoint
SECONDME_AUTH_ME_ENDPOINT=...      # from doc: auth-me endpoint
SECONDME_AUTH_REVOKE_WEBHOOK_SECRET=...   # required when revocation webhook is enabled
DATABASE_URL=...
```

## OAuth2 Rules

Fetch doc page for full OAuth2 flow details: https://develop-docs.second-me.cn/zh/docs/authentication/oauth2

Before implementing OAuth2, fetch the doc page above to get the current:

- authorization URL and query parameters
- token exchange endpoint, request format, and response shape
- auth-me endpoint and response shape
- token refresh endpoint and response shape
- authorization revocation webhook event fields, signature headers, and retry behavior
- token types, prefixes, and validity periods
- available scopes

Behavioral rules (apply regardless of API shape):

- OAuth URL already contains the full path; append `?` and query parameters directly; do not append `/authorize`
- token exchange uses `application/x-www-form-urlencoded`, not JSON
- after token exchange, call the auth-me endpoint and persist `appScopedUserId` for the local account binding
- always check `result.code`; actual payload is under `result.data`
- response fields use camelCase
- `redirect_uri` in token exchange must exactly match the one used in the authorization request
- `appScopedUserId` is stable only within the current app; do not treat it as a cross-app or global user id

Example:

```typescript
const authUrl = `${process.env.SECONDME_OAUTH_URL}?${params.toString()}`;
```

## Recommended User Table Fields

Any implementation that persists user auth should retain at least:

- local `id`
- stable app-scoped auth identifier `appScopedUserId`
- upstream user id such as `secondmeUserId` or `oauthId` when the product also needs a platform-level identity reference
- `accessToken`
- `refreshToken`
- `tokenExpiresAt`
- timestamps

## Authorization Revocation Webhook

Fetch doc page for webhook event details: https://develop-docs.second-me.cn/zh/docs/authentication/oauth2

When the user's app relies on OAuth login or app-bound access, recommend implementing the authorization revocation webhook unless they explicitly do not want automatic local cleanup.

Behavioral rules:

- the event type is `authorization.revoked`
- persist `appScopedUserId` during login so the webhook can locate the local auth binding later
- verify the signature from the raw request body string; do not reconstruct JSON before signing
- verify `X-SecondMe-Timestamp` with a 5-minute tolerance window before processing
- use `eventId` as the idempotency key
- use `appScopedUserId` to locate the local binding, then revoke local sessions, account links, or access grants
- `reason = test_delivery` is a connectivity test and should not revoke a real user binding
- ordinary `4xx` responses are not retried by default; timeouts, connection failures, `408`, `429`, and `5xx` are retried
- return `2xx` only after signature checks and local processing are complete or the event has already been handled idempotently

Recommended server-side tests:

- valid signature and fresh timestamp are accepted
- invalid signature is rejected
- expired timestamp is rejected
- duplicate `eventId` is handled idempotently
- `reason = test_delivery` does not remove real auth state
- `reason = user_revoked` removes the expected local session or account binding

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

Do not guess or infer API paths from scope names. API paths do not follow an obvious naming convention (e.g. `userinfo` scope does not map to `/api/userinfo` — the actual path is `/api/secondme/user/info`).

Remote source of truth — always fetch the relevant doc page before writing code that calls any SecondMe API:

| Feature | Doc URL |
|---------|---------|
| Agent Memory | https://develop-docs.second-me.cn/zh/docs/secondme/agent-memory |
| Act | https://develop-docs.second-me.cn/zh/docs/secondme/act |
| Chat | https://develop-docs.second-me.cn/zh/docs/secondme/chat |
| Note | https://develop-docs.second-me.cn/zh/docs/secondme/note |
| Plaza | https://develop-docs.second-me.cn/zh/docs/secondme/plaza |
| TTS | https://develop-docs.second-me.cn/zh/docs/secondme/tts |
| User Info | https://develop-docs.second-me.cn/zh/docs/secondme/user |
| Visitor Chat | https://develop-docs.second-me.cn/zh/docs/secondme/visitor-chat |
| OAuth2 | https://develop-docs.second-me.cn/zh/docs/authentication/oauth2 |
| Error Codes | https://develop-docs.second-me.cn/zh/docs/errors |
| Changelog | https://develop-docs.second-me.cn/zh/docs/changelog |

Rules:

1. Before writing any code that calls SecondMe APIs, fetch the relevant doc page(s) from the table above
2. Use only the endpoint paths, parameters, and response shapes from the fetched docs — never invent or infer paths
3. If the fetch fails, inform the user that the doc site is unreachable and ask them to provide the API details or retry later
4. When debugging an API call failure, fetch both the relevant feature doc page and the error codes page

## Optional Capability References

Fetch the relevant doc page from the table above when the user needs any of these:

- `chat.read` / `chat.write`: streaming chat — fetch Chat doc page
- `chat.write` (act): structured JSON decision output — fetch Act doc page
- `note.write`: note creation — fetch Note doc page
- `agent_memory`: ingest and query events — fetch Agent Memory doc page
- `voice`: text-to-speech — fetch TTS doc page
- `plaza.read` / `plaza.write`: social feed — fetch Plaza doc page
- `userinfo` / `memory.read`: user profile and Key Memory — fetch User Info doc page
- visitor chat: anonymous or authenticated avatar dialog — fetch Visitor Chat doc page
