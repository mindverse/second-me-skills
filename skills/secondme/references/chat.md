# Chat

聊天有**两个目标**，先判断用户想和谁聊，再选链路：

| 目标 | 判断依据 | session 获取方式 | 链路 |
|------|----------|------------------|------|
| **自己的 SecondMe（默认）** | 用户说「和我的 SecondMe 聊」「问问我的分身」，或没有指明对象 | 查后端 `GET /chat/session/list` | 流式聊天 `/chat/stream`（下方 API Reference） |
| **某人的分身** | 用户给出分身链接（`https://second.me/{route}/avatar/{shareCode}`）或 shareCode，或点名要和某个分身聊 | 后端按 userId+mindId 自动查找或新建（服务端 find-or-create） | 分身会话聊天（见 [和某人的分身聊天](#和某人的分身聊天)） |

Session 一律**查后端接口**，不在本地文件里维护会话映射——后端是会话的唯一权威源。

---

## 和某人的分身聊天

根据分身链接或 shareCode，找到（或新建）自己和这个分身的会话，基于该会话聊天。

### 流程

1. **解析 shareCode**：分身链接取路径末段（`https://second.me/daihaochen/avatar/1cf5e7728beb` → `1cf5e7728beb`）；用户直接给 shareCode 就直接用。
2. **确认目标分身**：`GET {BASE}/api/secondme/avatar/public/{shareCode}` 取公开信息（name、ownerUsername 等），向用户确认「要和 {ownerUsername} 的分身『{name}』聊，对吗」——首次聊某个分身时确认一次即可，同一会话内不重复确认。
3. **发消息（session 由后端查找或新建）**：

   ```
   POST {BASE}/api/secondme/ws-chat/send
   ```

   | 参数 | 类型 | 必需 | 说明 |
   |------|------|------|------|
   | message | string | 是 | 消息文本 |
   | shareCode | string | 否 | 分身分享码。**传了发给该分身；不传则发给自己的个人 agent chat**。和分身聊必传 |
   | sessionId | string | 否 | 会话 ID；**首轮不传**——后端会按 userId+mind 查询已有会话并复用，没有才新建 |

   接口只接受这三个参数（多传会被 422 拒绝）。shareCode → 分身的解析由服务端完成（os-main `avatar/chat/init`），skill 不需要也不应该关心 mindId。

   **不要在本地维护会话映射**：不传 `sessionId` 时，后端的 find-or-create 就是「查询自己和这个分身的 session，没有就新建」的权威实现。

   响应（同步返回完整回复，无需处理流）：

   ```json
   { "code": 0, "data": { "replyText": "…", "replyTexts": ["…"], "sessionId": "…", "messageId": "…" } }
   ```

   `replyTexts` 是分身把一轮回复拆成多条时的有序列表，展示时逐条呈现。
4. **续聊**：同一对话内的后续轮次带上返回的 `sessionId` 调 `ws-chat/send`（省一次后端查询）；跨对话重来时不带 `sessionId`，让后端重新查找即可，历史会话不会丢。

### 视角说明（和自己的分身聊时）

用 `ws-chat/send` + 自己分身的 shareCode 聊天完全可行（独立会话，**场景人设生效**——pre 实测确认），但这是 **owner 视角**：分身认得你是主人，会直呼你的名字、自居「你的 Second Me」、可动用你的私有记忆。适合日常自用和验证场景/知识；**访客看到的效果**（开场白、对陌生人的称呼与边界）与此不同，要用分享链接在网页里以访客身份预览。

### 错误与降级

- 分身不存在 / 分享码无效：后端返回 `ws_chat.share_code.mind_not_found` 类错误，如实转告用户。
- 付费分身可能返回解锁/免费次数相关业务错误（`avatar.unlock.required` 等），提示用户打开分享链接在网页完成解锁后再聊。
- 若接口尚未支持 `shareCode` 参数（后端 MR 未合入环境）：请求会报参数校验错误——此时引导用户打开分享链接在网页里聊（裸 URL 单独一行），不要编造参数重试。

---

## API Reference（自己的 SecondMe）

### 流式聊天

以用户的 AI 分身进行流式对话。

```
POST {BASE}/api/secondme/chat/stream
```

#### 请求头

| 头 | 必需 | 说明 |
|---|------|------|
| Authorization | 是 | Bearer Token |
| Content-Type | 是 | application/json |
| X-App-Id | 否 | 应用 ID，默认 `general` |

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| message | string | 是 | 用户消息内容 |
| sessionId | string | 否 | 会话 ID，不提供则自动生成新会话 |
| appId | string | 否 | 应用 ID，优先级高于 Header |
| systemPrompt | string | 否 | 系统提示词，仅在新会话首次有效 |
| receiverUserId | number | 否 | 接收方用户 ID（预留字段） |
| enableWebSearch | boolean | 否 | 是否启用网页搜索，默认 false |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/chat/stream" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，介绍一下自己",
    "systemPrompt": "请用友好的语气回复"
  }'
```

**启用 WebSearch:**

```bash
curl -X POST "{BASE}/api/secondme/chat/stream" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "今天有什么科技新闻",
    "enableWebSearch": true
  }'
```

#### 响应

响应类型为 `text/event-stream` (Server-Sent Events)。

**新会话首条消息:**

```
event: session
data: {"sessionId": "labs_sess_a1b2c3d4e5f6"}

```

**聊天内容流:**

```
data: {"choices": [{"delta": {"content": "你好"}}]}

data: {"choices": [{"delta": {"content": "！我是"}}]}

data: {"choices": [{"delta": {"content": "你的 AI 分身"}}]}

data: [DONE]
```

**启用 WebSearch 时的事件流:**

```
event: session
data: {"sessionId": "labs_sess_a1b2c3d4e5f6"}

event: tool_call
data: {"toolName": "web_search", "status": "searching"}

event: tool_result
data: {"toolName": "web_search", "query": "科技新闻", "resultCount": 5}

data: {"choices": [{"delta": {"content": "根据搜索结果..."}}]}

data: [DONE]
```

#### 流数据格式

| 事件类型 | 说明 |
|---------|------|
| session | 新会话创建时返回会话 ID |
| tool_call | 工具调用开始，启用 WebSearch 时触发 |
| tool_result | 工具调用结果，包含搜索查询和结果数量 |
| data | 聊天内容增量 |
| [DONE] | 流结束标志 |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| secondme.user.invalid_id | 无效的用户 ID |
| secondme.stream.error | 流式响应错误 |

---

### 获取会话列表

获取用户的聊天会话列表。

```
GET {BASE}/api/secondme/chat/session/list
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| appId | string | 否 | 按应用 ID 筛选 |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/chat/session/list?appId=general" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "sessions": [
      {
        "sessionId": "labs_sess_a1b2c3d4",
        "appId": "general",
        "lastMessage": "你好，介绍一下自己...",
        "lastUpdateTime": "2024-01-20T15:30:00Z",
        "messageCount": 10
      }
    ]
  }
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| sessions | array | 会话列表，按最后更新时间倒序 |
| sessions[].sessionId | string | 会话 ID |
| sessions[].appId | string | 应用 ID |
| sessions[].lastMessage | string | 最后一条消息预览（截断至 50 字） |
| sessions[].lastUpdateTime | string | 最后更新时间（ISO 8601） |
| sessions[].messageCount | number | 消息数量 |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |

---

### 获取会话消息历史

获取指定会话的消息历史。

```
GET {BASE}/api/secondme/chat/session/messages
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| sessionId | string | 是 | 会话 ID |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/chat/session/messages?sessionId=labs_sess_a1b2c3d4" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "sessionId": "labs_sess_a1b2c3d4",
    "messages": [
      {
        "messageId": "msg_001",
        "role": "system",
        "content": "请用友好的语气回复",
        "senderUserId": 12345,
        "receiverUserId": null,
        "createTime": "2024-01-20T15:00:00Z"
      },
      {
        "messageId": "msg_002",
        "role": "user",
        "content": "你好，介绍一下自己",
        "senderUserId": 12345,
        "receiverUserId": null,
        "createTime": "2024-01-20T15:00:05Z"
      },
      {
        "messageId": "msg_003",
        "role": "assistant",
        "content": "你好！我是你的 AI 分身...",
        "senderUserId": 12345,
        "receiverUserId": null,
        "createTime": "2024-01-20T15:00:10Z"
      }
    ]
  }
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| sessionId | string | 会话 ID |
| messages | array | 消息列表，按创建时间升序 |
| messages[].messageId | string | 消息 ID |
| messages[].role | string | 角色：`system`/`user`/`assistant` |
| messages[].content | string | 消息内容 |
| messages[].senderUserId | number | 发送方用户 ID |
| messages[].receiverUserId | number | 接收方用户 ID（预留） |
| messages[].createTime | string | 创建时间（ISO 8601） |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| secondme.session.unauthorized | 无权访问该会话 |

> **注意**: 如果 sessionId 不存在，接口会返回成功（code=0），但 messages 为空数组。

---

## Behavioral Rules

- Session lookup is **API-first**: to continue a previous conversation, query `GET {BASE}/api/secondme/chat/session/list` and pick the right session (by `lastMessage` / `lastUpdateTime`, confirm with the user if ambiguous). Never maintain session mappings in local files — the backend is the single source of truth.
- When the user starts a new chat without a `sessionId`, watch for the `event: session` SSE event in the response; extract the returned `sessionId` and reuse it for subsequent turns within the same conversation
- `systemPrompt` is ignored on follow-up messages within the same session
- Do not send `receiverUserId`; it is a reserved internal field
- Only the session owner can read the messages; unauthorized access returns 403
