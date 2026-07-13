# Chat

所有聊天统一走一个接口。先判断目标，再决定是否传 `shareCode`：

| 目标 | 判断依据 | `shareCode` |
|------|----------|-------------|
| **Personal Agent（默认）** | 用户说「和我的 SecondMe 聊」「和我主分身聊」「和我的 Agent 聊」「问问我的分身」，或没有指明对象 | **不传**。即使传入主分身的 shareCode，后端也会路由到同一个 Personal Agent；skill 默认省略 |
| **其他指定分身** | 用户给出其他分身的分享链接、shareCode，或明确点名某个分身 | 传该分身的 shareCode |

不要查询会话列表，不要传递或维护 `sessionId`。后端根据当前登录用户和聊天目标处理会话。

## 聊天流程

### 1. 确定目标

- Personal Agent：直接发送消息，不需要先查主分身或任何会话接口。
- 其他指定分身：从分享链接路径末段解析 shareCode（例如 `https://second-me.cn/daihaochen/avatar/1cf5e7728beb` → `1cf5e7728beb`）；用户直接给 shareCode 时直接使用。
- 首次和其他指定分身聊天时，先调用 `GET {BASE}/api/secondme/avatar/public/{shareCode}` 获取 `name`、`ownerUsername` 等公开信息，确认目标正确。同一轮对话内无需重复确认。

### 2. 发送消息

```text
POST {BASE}/api/secondme/ws-chat/send
```

#### 请求头

| 头 | 必需 | 说明 |
|----|------|------|
| Authorization | 是 | `Bearer <accessToken>` |
| Content-Type | 是 | `application/json` |

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| message | string | 是 | 消息文本 |
| shareCode | string | 否 | 不传或传主分身 shareCode 时和 Personal Agent 聊；传其他分身 shareCode 时和该分身聊 |

接口请求体只需要 `message` 和可选的 `shareCode`。**不要传 `sessionId`、`mindId` 或其他会话参数。**

Personal Agent：

```bash
curl -X POST "{BASE}/api/secondme/ws-chat/send" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"你好，介绍一下自己"}'
```

其他指定分身：

```bash
curl -X POST "{BASE}/api/secondme/ws-chat/send" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"你好，介绍一下自己","shareCode":"1cf5e7728beb"}'
```

#### 响应

接口同步返回完整回复：

```json
{
  "code": 0,
  "data": {
    "replyText": "…",
    "replyTexts": ["…"],
    "messageId": "…"
  }
}
```

`replyTexts` 是一轮回复拆成多条时的有序列表，展示时逐条呈现；若只有 `replyText`，直接展示该字段。后续消息继续按相同目标调用本接口，无需携带会话 ID。

## 错误处理

- 分身不存在或分享码无效：后端返回 `ws_chat.share_code.mind_not_found` 一类错误，如实告知用户并请其检查分享链接。
- 付费分身要求解锁或免费次数耗尽：提示用户打开该分身的分享链接，在网页完成解锁后再聊。
- 公开信息与用户点名的目标不一致：不要发送消息，先请用户确认目标。

## Behavioral Rules

- 「我的 SecondMe」「我的主分身」「我的 Agent」都是 Personal Agent 的同义表达，默认不传 `shareCode`。
- 主分身 shareCode 不是另一条聊天链路；即使用户提供了它，语义仍是 Personal Agent。
- 只有其他指定分身需要传 `shareCode`。
- 聊天只调用 `POST {BASE}/api/secondme/ws-chat/send`，不再调用其他聊天接口。
- 不读取、保存、推断或传递 `sessionId`；服务端是会话状态的唯一维护方。
