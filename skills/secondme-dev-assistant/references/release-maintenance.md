# Release & Maintenance (Phase 9) + Confirmation Rules

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
- explain that AI clients can then use that integration to access the app's exposed MCP tools
- if the user's goal is AI client usage, explicitly say that integration approval is the milestone that enables that path

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
