# Chat

## API Reference

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

- When the user starts a new chat without a `sessionId`, watch for the `event: session` SSE event in the response; extract and store the returned `sessionId` for subsequent requests
- `systemPrompt` is ignored on follow-up messages within the same session
- Do not send `receiverUserId`; it is a reserved internal field
- Only the session owner can read the messages; unauthorized access returns 403
