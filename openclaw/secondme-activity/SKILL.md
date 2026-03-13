---
name: secondme-openclaw-activity
description: Use when the user wants the SecondMe day overview, today's activity, or a specific date's activity summary in OpenClaw
user-invocable: true
---

# SecondMe OpenClaw Activity

**Credentials file:** `{baseDir}/.credentials`

## Authentication Prerequisite

Before using this skill, read `{baseDir}/.credentials`.

- If it contains `accessToken`, continue
- If it only contains legacy `access_token`, continue but normalize later
- If the file is missing, empty, or invalid, switch to `secondme-openclaw-connect`

## Day Overview

Use:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/agent/events/day-overview?date=<yyyy-MM-dd>&pageNo=1&pageSize=10
Authorization: Bearer <token>
```

Rules:
- `date` is optional and uses `yyyy-MM-dd`
- default `pageNo` is `1`
- default `pageSize` is `10`
- use the returned structure as-is

When presenting results, summarize the day's important items in chronological order.
