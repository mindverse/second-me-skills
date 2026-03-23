# Control Plane Operations (Phase 6, 7 & 8)

## Contents

- [Phase 6: CLI Auth](#phase-6-authenticate-with-secondme-develop-cli-auth)
- [Phase 7: Manage External OAuth Apps](#phase-7-manage-external-oauth-apps-on-secondme-develop)
  - [Developer Routes](#developer-routes)
  - [Public Routes](#public-routes)
  - [Create Request Shape](#create-request-shape)
  - [Update Request Shape](#update-request-shape)
  - [External App Rules](#external-app-rules)
  - [Listing Media URL Handling](#listing-media-url-handling)
  - [Apply-Listing Review Guidance](#apply-listing-review-guidance)
- [Phase 8: Manage Integrations](#phase-8-manage-integrations-on-secondme-develop)
  - [Integration Developer Routes](#integration-developer-routes)
  - [Manifest Shape](#manifest-shape)
  - [Field Rules](#field-rules)
  - [Create vs Update Rules](#create-vs-update-rules)

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

### Developer Routes

- `GET /applications/external/list`
- `GET /applications/external/{appId}`
- `POST /applications/external/create`
- `POST /applications/external/{appId}/update`
- `POST /applications/external/{appId}/regenerate-secret`
- `POST /applications/external/{appId}/delete`
- `POST /applications/external/{appId}/apply-listing`

### Public Routes

- `GET /applications/external/public/list`
- `GET /applications/external/{appId}/public`

### Create Request Shape

```json
{
  "appName": "Example App",
  "appDescription": "Optional description",
  "redirectUris": ["https://example.com/oauth/callback"],
  "allowedScopes": ["user.info"]
}
```

### Update Request Shape

```json
{
  "appName": "Example App",
  "appDescription": "Optional description",
  "redirectUris": ["https://example.com/oauth/callback"],
  "allowedScopes": ["user.info", "chat"]
}
```

### External App Rules

- default to operating on behalf of the user once auth is available
- always list apps before deciding a new app must be created
- if one app is an obvious match, present it for confirmation
- if multiple apps are plausible, show a short ranked list and ask the user to choose
- if no app exists yet, collect the required creation fields and create it directly instead of telling the user to do it manually
- only switch to self-serve instructions when the user explicitly wants to operate manually or the assistant is blocked by missing permissions or missing required inputs
- when app info or listing info is incomplete, ask targeted follow-up questions and draft the form values yourself instead of asking the user to fill the full form manually
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

### Integration Developer Routes

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

### Manifest Shape

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

### Field Rules

- `skill.key` is blocking and must be stable
- if the user explicitly asks for a new key, treat it as a new integration candidate
- `toolName` must match the actual MCP tool name exactly
- `authMode` must be one of `none`, `bearer_token`, or `header_template`
- `oauth.appId` must be user-confirmed
- `envBindings.release.endpoint` must be user-confirmed
- `envSecrets.release.values` must contain only values actually required by endpoint or header templates

### Create vs Update Rules

- if the user or repo already identifies an integration id, treat it as an update candidate
- otherwise list integrations and match by `skill.key` plus confirmed project identity
- if exactly one strong match exists, present it as the update target
- if there is no match, prepare a create payload
- if there are multiple plausible matches, ask the user which one to update
- when manifest fields are incomplete, gather the missing facts and draft the integration payload yourself; do not default to telling the user to author the whole manifest manually
