# Key Memory

## Contents

- [Overview](#overview)
- [Guided Memory Sync](#guided-memory-sync)
- [Insert Key Memory](#insert-key-memory)
- [Batch Create Key Memory](#batch-create-key-memory)
- [Search Key Memory](#search-key-memory)
- [Update Key Memory](#update-key-memory)
- [Delete Key Memory](#delete-key-memory)

## Overview

This section is only for explicit SecondMe Key Memory operations.

If the user only says generic `记忆`, `memory`, `你记得吗`, or `查我的记忆`, do not assume they mean this section. That wording may refer to OpenClaw local memory.

If ambiguous, ask:

> 你要查 OpenClaw 本地记忆，还是 SecondMe 的 Key Memory？

## Guided Memory Sync

If the user is in onboarding, or asks how to shape their SecondMe faster, offer:

> 如果你愿意，我可以把 OpenClaw 里适合长期保存的记忆整理成几条，再分条存进 SecondMe。
>
> 这样通常能更快塑造你的 SecondMe。
>
> 要我先整理一版给你确认吗？

Rules:

- ask for consent before preparing or writing a sync batch
- if the user accepts from the first-login handoff, first review OpenClaw local memory and extract candidate facts that are suitable for long-term storage in SecondMe
- if there are no suitable local memory facts, say so clearly and do not push the import step
- if the user agrees, first show the candidate facts in a compact list
- only write the facts the user confirms
- prefer durable facts such as preferences, stable background, and long-term context
- for this onboarding sync flow, use the batch create endpoint below after the user confirms the list
- after batch create succeeds, report the returned `insertedCount`

## Insert Key Memory

Direct mode:

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/memories/key
Content-Type: application/json
Authorization: Bearer <accessToken>
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
- durable relationship or context facts

## Batch Create Key Memory

Use batch create when the user confirms multiple memory items at once:

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/memories/key/batch
Content-Type: application/json
Authorization: Bearer <accessToken>
Body: {
 "items": [
  {
   "content": "<memory content>",
   "visibility": 1
  }
 ]
}
```

Response:

- `insertedCount`

## Search Key Memory

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/memories/key/search?keyword=<keyword>&pageNo=1&pageSize=20
Authorization: Bearer <accessToken>
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

## Update Key Memory

```
PUT https://app.mindos.com/gate/in/rest/third-party-agent/v1/memories/key/{memoryId}
Content-Type: application/json
Authorization: Bearer <accessToken>
Body: {
 "content": "<updated memory content>",
 "visibility": 1
}
```

Rules:

- `memoryId` is a numeric memory identifier
- update only after the user confirms which memory to change
- only send the fields the user wants changed

## Delete Key Memory

```
DELETE https://app.mindos.com/gate/in/rest/third-party-agent/v1/memories/key/{memoryId}
Authorization: Bearer <accessToken>
```

Rules:

- `memoryId` is a numeric memory identifier
- confirm the deletion target with the user before calling delete
