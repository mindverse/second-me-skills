---
name: secondme-openclaw-discover
description: Use when the user wants to discover nearby users or browse people through the SecondMe OpenClaw discover API
user-invocable: true
---

# SecondMe OpenClaw Discover

**Credentials file:** `{baseDir}/.credentials`

## Authentication Prerequisite

Before using this skill, read `{baseDir}/.credentials`.

- If it contains `accessToken`, continue
- If it only contains legacy `access_token`, continue but normalize later
- If the file is missing, empty, or invalid, switch to `secondme-openclaw-connect`

## Discover Users

This API supports discover-style browsing, not free-text semantic people search.

`discover/users` may respond slowly. When calling it:

- If the caller supports a configurable timeout or wait window, set it to at least `60s` for this request
- Do not treat the request as failed before that wait window expires
- If the first attempt ends with a clear timeout or transient network timeout, retry once before surfacing failure
- If the caller has a hard timeout below `60s`, explain that the failure is likely caused by the runtime timeout rather than invalid discover parameters

Use:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/discover/users?pageNo=1&pageSize=20
Authorization: Bearer <token>
```

Optional query params:
- `longitude`
- `latitude`
- `circleType`

Present useful fields such as:
- `username`
- `distance`
- `route`
- `matchScore`
- `title`
- `hook`
- `briefIntroduction`

When presenting recommended users:

- Always include a personal homepage link for each user
- Build that homepage as `https://second-me.cn/{route}`
- Do not show only the raw `route`
- If `route` is missing or blank, say clearly that the user's homepage is currently unavailable

If the user asks for highly specific semantic matching, explain that the current interface is discover-style browsing rather than free-text people search.
