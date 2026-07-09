# Chat

聊天有**两个目标**，先判断用户想和谁聊，再选链路：

| 目标 | 判断依据 | 链路 |
|------|----------|------|
| **自己的 SecondMe（默认）** | 用户说「和我的 SecondMe 聊」「问问我的分身」，或没有指明对象 | 流式聊天 `/chat/stream`（下方 API Reference） |
| **某人的分身** | 用户给出分身链接（`https://second-me.cn/{route}/avatar/{shareCode}`）或 shareCode，或点名要和某个分身聊 | 分身会话聊天（见 [和某人的分身聊天](#和某人的分身聊天)） |

---

## 和某人的分身聊天

根据分身链接或 shareCode，找到（或新建）自己和这个分身的会话，基于该会话聊天。

### 流程

1. **解析 shareCode**：分身链接取路径末段（`https://second-me.cn/daihaochen/avatar/1cf5e7728beb` → `1cf5e7728beb`）；用户直接给 shareCode 就直接用。
2. **确认目标分身**：`GET {BASE}/api/secondme/avatar/public/{shareCode}` 取公开信息（name、ownerUsername 等），向用户确认「要和 {ownerUsername} 的分身『{name}』聊，对吗」——首次聊某个分身时确认一次即可，同一会话内不重复确认。
3. **查询已有会话**：读本地会话映射文件 `~/.secondme/avatar-sessions.json`（结构：`{ "<shareCode>": { "sessionId": "...", "mindId": "...", "name": "..." } }`）。命中则复用其中的 `sessionId` 和 `mindId`。
4. **发消息（同步拿回复）**：

   ```
   POST {BASE}/api/secondme/ws-chat/send
   ```

   | 参数 | 类型 | 必需 | 说明 |
   |------|------|------|------|
   | mindId | string | 是 | 分身的 mind ID |
   | message | string | 是 | 消息文本 |
   | sessionId | string | 否 | 会话 ID；不传则后端新建会话 |

   响应（同步返回完整回复，无需处理流）：

   ```json
   { "code": 0, "data": { "replyText": "…", "replyTexts": ["…"], "sessionId": "…", "messageId": "…" } }
   ```

   - `replyTexts` 是分身把一轮回复拆成多条时的有序列表，展示时逐条呈现。
   - 首次发送后，把返回的 `sessionId` 连同 `mindId`、分身名写回 `~/.secondme/avatar-sessions.json`——这就是「没有 session 就新建一个」的落点，之后同一分身续聊都带这个 `sessionId`。
5. **续聊**：后续每轮都带保存的 `sessionId` 调 `ws-chat/send`，会话上下文由后端维持。

### mindId 解析（当前限制）

`ws-chat/send` 需要 `mindId`，而公开信息接口目前**不返回 mindId**（shareCode → mindId 的解析接口 `avatar/chat/init` 在 os-main 侧，labs 尚未透出）。处理顺序：

1. 本地映射文件里有该 shareCode 的 `mindId` → 直接用。
2. 尝试 `GET {BASE}/api/secondme/avatar/public/{shareCode}`，若响应里带 `mindId` 类字段 → 用并写回映射文件。
3. 都拿不到 → 如实告诉用户「该分身的会话初始化能力还在建设中，目前可以打开分享链接在网页里聊」，输出分享链接（裸 URL 单独一行），不要编造 mindId。

> 后端待办（已记录于 spec）：`ws-chat/send` 支持传 `shareCode` 替代 `mindId`（服务端用用户 token 调 os-main `avatar/chat/init` 解析，微信 bot 模块已有同款实现可参照）。该能力上线后删除本节的 fallback。

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

- When the user starts a new chat without a `sessionId`, watch for the `event: session` SSE event in the response; extract and store the returned `sessionId` for subsequent requests
- `systemPrompt` is ignored on follow-up messages within the same session
- Do not send `receiverUserId`; it is a reserved internal field
- Only the session owner can read the messages; unauthorized access returns 403
