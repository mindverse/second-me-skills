# Requirements & Scaffold Plan (Phase 3)

## Contents

- [Standard Planning Mode](#standard-planning-mode)
- [Quick Start Mode](#quick-start-mode)
- [Output Of This Phase](#output-of-this-phase)
- [Optional Local Handoff Artifacts](#optional-local-handoff-artifacts)

When the user wants to build a SecondMe app, do requirement discovery before project generation.

Collect:

- product goal
- target users
- chosen modules
- key user flows
- preferred UI tone
- storage needs
- whether local auth/session state must be revoked when the user disconnects the app in SecondMe
- whether they want a quick start or a fuller requirements pass

## Standard Planning Mode

Use when the user wants a thoughtful project plan.

Clarify:

- what problem the app solves
- who uses it
- what the minimum useful feature set is
- which SecondMe capabilities are actually needed
- what local persistence is required
- whether the app should handle `authorization.revoked` webhook events from SecondMe
- what kind of review submission they eventually want

## Quick Start Mode

Use when the user wants a fast setup and accepts defaults.

Defaults:

- framework: Next.js with App Router
- language: TypeScript
- styling: Tailwind CSS
- ORM: Prisma
- local dev port: `3000`
- backend style: Next.js route handlers as proxy or app API layer

## Output Of This Phase

Do not jump straight into code generation. Produce a concrete build brief that the user's coding tool can execute.

The brief should include:

- app summary
- selected modules
- recommended stack
- required pages and API routes
- database tables
- environment variables
- OAuth flow steps
- webhook receiver route and revoke handling behavior when OAuth login is in scope
- MCP or integration requirements if relevant
- test checklist

## Optional Local Handoff Artifacts

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
    "allowedScopes": ["userinfo", "chat.read", "chat.write"],
    "authorizationRevokedWebhookUrl": "https://example.com/api/webhooks/secondme/revoked",
    "authorizationRevokedWebhookEnabled": true
  },
  "api": {
    "baseUrl": "https://api.mindverse.com/gate/lab",
    "oauthUrl": "https://go.second.me/oauth/",
    "tokenEndpoint": "https://api.mindverse.com/gate/lab/api/oauth/token/code",
    "refreshEndpoint": "https://api.mindverse.com/gate/lab/api/oauth/token/refresh",
    "authMeEndpoint": "https://api.mindverse.com/gate/lab/api/auth/me"
  },
  "docs": {
    "quickstart": "https://develop-docs.second-me.cn/zh/docs",
    "oauth2": "https://develop-docs.second-me.cn/zh/docs/authentication/oauth2",
    "apiReference": "https://develop-docs.second-me.cn/llms-full.txt",
    "errors": "https://develop-docs.second-me.cn/zh/docs/errors"
  },
  "prd": {
    "summary": "",
    "features": [],
    "targetUsers": "",
    "designPreference": "",
    "revokeHandling": true
  },
  "auth": {
    "persistAppScopedUserId": true,
    "webhookSecretStored": false
  }
}
```
