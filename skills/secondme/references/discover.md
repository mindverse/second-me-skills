# Discover

## Contents

- [Usage](#usage)
- [Presentation Rules](#presentation-rules)

## Usage

This API supports discover-style browsing, not free-text semantic people search.

`discover/users` may respond slowly. When calling it:

- If the caller supports a configurable timeout or wait window, set it to at least `60s` for this request
- Do not treat the request as failed before that wait window expires
- If the first attempt ends with a clear timeout or transient network timeout, retry once before surfacing failure
- If the caller has a hard timeout below `60s`, explain that the failure is likely caused by the runtime timeout rather than invalid discover parameters

Use:

```
GET {BASE}/api/secondme/discover/users?pageNo=1&pageSize=20
Authorization: Bearer <accessToken>
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

## Presentation Rules

When presenting recommended users:

- Always include a personal homepage link for each user
- Build that homepage as `https://second-me.cn/{route}`
- Do not show only the raw `route`
- If `route` is missing or blank, say clearly that the user's homepage is currently unavailable

If the user asks for highly specific semantic matching, explain that the current interface is discover-style browsing rather than free-text people search.

If the user asks to directly chat with those users, remind them that if they want to chat with people they are interested in, they can download SecondMe App, and output:

```
https://go.second.me
```
