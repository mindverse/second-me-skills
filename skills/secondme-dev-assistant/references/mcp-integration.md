# MCP & Integration Implementation Guidance (Phase 5)

## Contents

- [Platform Model](#platform-model)
- [Client Routing Guidance](#client-routing-guidance)
- [Repository Scan Rules](#repository-scan-rules)
- [MCP Suitability Guidance](#mcp-suitability-guidance)
- [MCP Runtime Auth Rules](#mcp-runtime-auth-rules)
- [Recommended Tests](#recommended-tests)

When the user needs MCP or SecondMe integration support, guide them toward the smallest valid MCP surface.

Fetch doc page for MCP/OpenClaw integration details: https://develop-docs.second-me.cn/zh/docs/mcp-integration

## Platform Model

Important platform model:

- SecondMe already provides the unified MCP server layer for platform integrations
- an application does not need to build a separate platform-level MCP server from scratch
- the application only needs to expose the required MCP-compatible interfaces or tool endpoints
- this skill then helps register those capabilities as a SecondMe integration and submit them for review
- once approved, other agents can call the application's exposed tools through the platform

## Client Routing Guidance

If the user asks how to use their own app through an AI client, guide them through the real platform path instead of answering abstractly.

Use this explanation:

1. the app capability must be exposed through MCP-compatible interfaces or endpoints
2. those MCP-compatible capabilities must be submitted to SecondMe as an integration
3. the integration must pass review
4. once approved, the app's integration can be discovered through the official skill third-party app list on the SecondMe platform
5. after it becomes discoverable there, the AI client can use the integration and call the app's exposed functionality

Routing rules for this request shape:

- if the user asks how an AI client can use their app, first confirm whether the app already exposes MCP-compatible interfaces or endpoints
- if it does not yet expose them, guide the user to add those interfaces first
- if those interfaces already exist, continue with integration create, validate, and release guidance
- if they only have a normal OAuth app and no MCP-compatible tool surface, explain that app creation alone is not enough for AI client tool usage and that an integration-facing MCP interface is still required

## Repository Scan Rules

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

## MCP Suitability Guidance

If no MCP-compatible interface exists yet, do not stop there.

Propose:

- the minimum useful tool set, usually `2-5` tools
- the actual tool names
- user-facing purpose
- input shape
- output shape
- auth requirement
- backing route or code path

Recommend one of:

- an HTTP MCP-compatible endpoint inside the existing app
- a thin MCP adapter layer that calls the existing app over HTTP

Do not imply that the app team must recreate the whole SecondMe MCP server stack.
The app only needs the exposed tool interfaces that can be registered through this skill as an integration.

## MCP Runtime Auth Rules

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

## Recommended Tests

- missing bearer token rejects the request
- invalid bearer token maps to `401`
- existing upstream user resolves correctly
- new upstream user is upserted correctly
- MCP-to-app forwarding preserves `Authorization`
- ownership violations return `403`
