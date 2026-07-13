# Open APIs for Third-Party Developers

API endpoint specifications are maintained on the documentation site and must be fetched at runtime.
Do not rely on memorized or cached API specs — always fetch the latest docs before implementing or troubleshooting.

## Contents

- [Agent Memory](#agent-memory)
- [Act (Structured Action)](#act-structured-action)

## Agent Memory

Third-party apps can ingest and query Agent Memory events on behalf of the authenticated user. These events feed into the CTA (Call-To-Action) orchestrator and build the user's activity graph.

Fetch doc page: https://develop-docs.second-me.cn/zh/docs/secondme/agent-memory

Before implementing or troubleshooting Agent Memory API calls, fetch the doc page above to get the current:

- endpoint path and method
- request body structure (channel, action, refs, and all optional fields)
- response fields (eventId, isDuplicate)
- error codes

Behavioral rules (apply regardless of API shape):

- `userId` is extracted from the auth token automatically; do not include it in the request body
- `channel.platform` defaults to the resolved `app_id` if omitted; do not manually set it
- `idempotencyKey` prevents duplicate ingestion; generate one if not provided by the caller
- always include `snapshot.text` in refs for better recall quality
- importance scoring guideline: routine 0.3-0.5, important 0.6-0.8, critical 0.9-1.0
- handle `isDuplicate: true` responses gracefully without treating them as errors

## Act (Structured Action)

The Act endpoint instructs the user's SecondMe to output a structured JSON judgment instead of freeform text. Use it when your app needs a machine-readable decision from the AI.

Fetch doc page: https://develop-docs.second-me.cn/zh/docs/secondme/act

Before implementing or troubleshooting Act API calls, fetch the doc page above to get the current:

- endpoint path and method
- request body structure (message, actionControl, sessionId, model, etc.)
- actionControl validation rules and length constraints
- response format (SSE stream)
- error codes

Behavioral rules (apply regardless of API shape):

- do not send `receiverUserId`; it is a reserved internal field
- use JSON boolean `true`/`false`, not string `"True"`/`"False"` in actionControl examples
- `actionControl` must include: output format constraint (JSON only), JSON field structure example with braces, judgment rules, and fallback rules for insufficient evidence
- the response error object includes `constraints`, `issues`, and `suggestions` fields to help fix invalid actionControl
