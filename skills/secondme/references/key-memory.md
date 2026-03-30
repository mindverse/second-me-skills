# Key Memory

## API Reference

### 插入 Key Memory

创建一条 Key Memory。

```
POST {BASE}/api/secondme/memory/key
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| content | string | 是 | 记忆内容（最长 5000 字符） |
| visibility | int | 否 | 可见性，`1` 为可见（默认: 1） |
| mode | string | 否 | 固定值 `direct`（默认: "direct"） |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/memory/key" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "direct",
    "content": "喜欢在周末阅读科幻小说",
    "visibility": 1
  }'
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {}
}
```

返回空对象表示创建成功。

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| memory.content.required | 缺少 content 字段 |

---

### 搜索 Key Memory

按关键词搜索 Key Memory，支持分页。

```
GET {BASE}/api/secondme/memory/key/search
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词 |
| pageNo | integer | 否 | 页码（默认: 1） |
| pageSize | integer | 否 | 每页大小（默认: 20） |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/memory/key/search?keyword=阅读&pageNo=1&pageSize=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": 12345,
        "factActor": "用户",
        "factObject": "兴趣爱好",
        "factContent": "喜欢在周末阅读科幻小说",
        "createTime": 1705315800000,
        "updateTime": 1705315800000,
        "visibility": 1
      }
    ],
    "total": 1
  }
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| list | array | Key Memory 列表 |
| list[].id | number | 记忆 ID |
| list[].factActor | string | 事实主体 |
| list[].factObject | string | 事实对象/分类 |
| list[].factContent | string | 事实内容 |
| list[].createTime | number | 创建时间（毫秒时间戳） |
| list[].updateTime | number | 更新时间（毫秒时间戳） |
| list[].visibility | number | 可见性 |
| list[].userId | number | 用户 ID |
| list[].dataType | string | 数据类型 |
| list[].memoryKind | string | 记忆分类 |
| list[].readStatus | string | 已读状态 |
| list[].memoryState | string | 记忆状态 |
| total | number | 总数 |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |

---

### 更新 Key Memory

更新指定的 Key Memory 内容。

```
POST {BASE}/api/secondme/memory/key/{memory_id}/update
```

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| memory_id | number | 是 | Key Memory ID |

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| content | string | 否 | 更新后的记忆内容 |
| visibility | number | 否 | 可见性，`1` 为可见 |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/memory/key/12345/update" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "喜欢在周末阅读科幻小说和技术书籍",
    "visibility": 1
  }'
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": null
}
```

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| memory.not_found | 指定的 Key Memory 不存在 |

---

### 删除 Key Memory

删除指定的 Key Memory。

```
POST {BASE}/api/secondme/memory/key/{memory_id}/delete
```

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| memory_id | number | 是 | Key Memory ID |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/memory/key/12345/delete" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": null
}
```

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| memory.not_found | 指定的 Key Memory 不存在 |

---

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

If the user only says generic `记忆`, `memory`, `你记得吗`, or `查我的记忆`, do not assume they mean this section. That wording may refer to local memory (the assistant's own memory of the user).

If ambiguous, ask:

> 你要查本地记忆，还是 SecondMe 的 Key Memory？

## Guided Memory Sync

If the user is in onboarding, or asks how to shape their SecondMe faster, offer:

> 如果你愿意，我可以把适合长期保存的记忆整理成几条，再分条存进 SecondMe。
>
> 这样通常能更快塑造你的 SecondMe。
>
> 要我先整理一版给你确认吗？

Rules:

- ask for consent before preparing or writing a sync batch
- if the user accepts from the first-login handoff, first review local memory and extract candidate facts that are suitable for long-term storage in SecondMe
- if there are no suitable local memory facts, say so clearly and do not push the import step
- if the user agrees, first show the candidate facts in a compact list
- only write the facts the user confirms
- prefer durable facts such as preferences, stable background, and long-term context
- for this onboarding sync flow, use the batch create endpoint below after the user confirms the list
- after batch create succeeds, report the returned `insertedCount`

## Insert Key Memory

Use Key Memory for durable facts like:

- user preferences
- stable biographical facts
- durable relationship or context facts

## Batch Create Key Memory

Use batch create when the user confirms multiple memory items at once.

There is no dedicated batch endpoint. To insert multiple memories, call the single insert endpoint once per item. Send one request per memory item sequentially. After all requests complete, report how many were inserted successfully.

## Search Key Memory

Do not merge local memory results with SecondMe Key Memory results unless the user explicitly asks for both.

## Update Key Memory

Rules:

- update only after the user confirms which memory to change
- only send the fields the user wants changed

## Delete Key Memory

Rules:

- confirm the deletion target with the user before calling delete
