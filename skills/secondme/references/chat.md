# Chat

所有聊天统一走一个接口。Skill 只负责传递用户明确提供的 `shareCode`，不判断它属于主分身还是其他分身：

- 用户说「和我的小己聊」「和我的 Second Me 聊」「和我主分身聊」「和我的 Agent 聊」「问问我的分身」，或没有指明对象和 shareCode：不传 `shareCode`。
- 用户明确提供分身分享链接或 shareCode：解析后原样传给后端。

## 聊天流程

### 1. 组装参数

- 用户没有明确提供 shareCode：只传 `message`。
- 用户给出对外分享链接或创作者测试链接：取 `/avatar/` 后的第一段作为 `shareCode`，忽略测试链接末尾的 `/test`（例如 `https://second-me.cn/daihaochen/avatar/1cf5e7728beb/test` → `1cf5e7728beb`）。
- 用户直接给出 shareCode：将其原样传入。

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
| shareCode | string | 否 | 用户明确提供分享链接或 shareCode 时传入；聊天目标由后端判断 |

用户未提供 shareCode：

```bash
curl -X POST "{BASE}/api/secondme/ws-chat/send" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"你好，介绍一下自己"}'
```

用户明确提供 shareCode：

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

## Behavioral Rules

- 「我的小己」「我的 Second Me」「我的主分身」「我的 Agent」都是 Personal Agent 的同义表达，默认不传 `shareCode`。
- 不查询或比较主分身 shareCode，不在 Skill 侧判断 shareCode 对应哪类分身。
- 用户明确提供 shareCode 时原样传入，由后端决定聊天目标。
- 聊天只调用 `POST {BASE}/api/secondme/ws-chat/send`，不再调用其他聊天接口。
