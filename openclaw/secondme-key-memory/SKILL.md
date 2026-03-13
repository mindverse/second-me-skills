---
name: secondme-openclaw-key-memory
description: Use when the user explicitly says Key Memory, SecondMe memory, or wants to save or search durable facts in SecondMe rather than OpenClaw local memory
user-invocable: true
---

# SecondMe OpenClaw Key Memory

This skill is only for explicit SecondMe Key Memory operations.

If the user only says generic `记忆`, `memory`, `你记得吗`, or `查我的记忆`, do not assume they mean this skill. That wording may refer to OpenClaw local memory.

If ambiguous, ask:

> 你要查 OpenClaw 本地记忆，还是 SecondMe 的 Key Memory？

**Credentials file:** `{baseDir}/.credentials`

## Authentication Prerequisite

Before using this skill, read `{baseDir}/.credentials`.

- If it contains `accessToken`, continue
- If it only contains legacy `access_token`, continue but normalize later
- If the file is missing, empty, or invalid, switch to `secondme-openclaw-connect`

## Insert Key Memory

Direct mode:

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/memories/key
Content-Type: application/json
Authorization: Bearer <token>
Body: {
 "mode": "direct",
 "content": "<memory content>",
 "visibility": 1
}
```

Extraction mode:

```json
{
 "mode": "extract",
 "content": "<source content>",
 "context": "<optional>",
 "source": "<required>",
 "sourceId": "<required>"
}
```

Use Key Memory for durable facts like:
- user preferences
- stable biographical facts
- durable relationship/context facts

## Search Key Memory

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/memories/key/search?keyword=<keyword>&pageNo=1&pageSize=20
Authorization: Bearer <token>
```

Common response fields:
- `list`
- `total`

Useful item fields:
- `factActor`
- `factObject`
- `factContent`
- `createTime`
- `updateTime`
- `visibility`

Do not merge OpenClaw local memory results with SecondMe Key Memory results unless the user explicitly asks for both.
