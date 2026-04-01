# Friend

## API Reference

### 好友列表

获取当前用户的好友列表，支持分页。

```
GET {BASE}/api/secondme/friend/list
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| type | string | 否 | 关系类型，默认 `FRIEND` |
| pageNo | integer | 否 | 页码（默认: 1） |
| pageSize | integer | 否 | 每页大小（默认: 20，最大: 100） |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/friend/list?type=FRIEND&pageNo=1&pageSize=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "friends": [
      {
        "friendId": "friend_001",
        "name": "好友A",
        "avatar": "https://cdn.example.com/avatar.jpg",
        "sessionId": "sess_12345",
        "relationType": "two-way-friend",
        "latestMessage": "你好，最近怎么样？",
        "latestMessageTime": 1705315800000,
        "unreadCount": 2,
        "route": "friendA",
        "source": "DISCOVER"
      }
    ],
    "total": 15,
    "friendInvitation": {
      "pendingCount": 3
    },
    "totalUnreadCount": 5
  }
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| friends | array | 好友列表 |
| friends[].friendId | string | 好友用户 ID |
| friends[].name | string | 好友名称 |
| friends[].avatar | string | 好友头像 URL |
| friends[].sessionId | string | 私聊会话 ID |
| friends[].relationType | string | 关系类型，如 `two-way-friend` |
| friends[].latestMessage | string | 最近一条消息预览 |
| friends[].latestMessageTime | number | 最近消息时间（毫秒时间戳） |
| friends[].unreadCount | number | 未读消息数 |
| friends[].route | string | 好友主页路由 |
| friends[].source | string | 好友来源 |
| friends[].label | string | 标签 |
| friends[].blockedByMe | boolean | 是否被我拉黑 |
| friends[].isBlocked | boolean | 是否被对方拉黑 |
| friends[].sourceDirection | string | 来源方向 |
| total | number | 好友总数 |
| friendInvitation | object | 待处理的好友邀请摘要 |
| totalUnreadCount | number | 总未读消息数 |
| strangerMessage | object | 陌生人消息信息 |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |

---

### 发送好友邀请

向指定用户发送好友邀请。

```
POST {BASE}/api/secondme/friend/invite/send
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| targetUserId | string | 是 | 目标用户 ID |
| greeting | string | 否 | 打招呼消息（最长 500 字符） |
| source | string | 否 | 来源标识，如 `DISCOVER`、`PLAZA` |
| sourceData | object | 否 | 来源附加数据 |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/friend/invite/send" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "targetUserId": "user_12345",
    "greeting": "你好，在 Discover 看到你的介绍，很想认识你！",
    "source": "DISCOVER"
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
| friend.invite.already_sent | 已经发送过好友邀请 |
| friend.invite.already_friend | 已经是好友关系 |

---

### 处理好友邀请

接受或拒绝收到的好友邀请。

```
POST {BASE}/api/secondme/friend/invite/handle
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| targetUserId | string | 是 | 发送邀请的用户 ID |
| action | string | 是 | 处理动作：`ACCEPTED`（接受）或 `REJECTED`（拒绝） |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/friend/invite/handle" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "targetUserId": "user_12345",
    "action": "ACCEPTED"
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
| friend.invite.not_found | 好友邀请不存在 |
| friend.invite.already_handled | 邀请已被处理 |

---

### 破冰对话

发起与好友的破冰对话，生成 AI 驱动的开场消息帮助开始聊天。

```
POST {BASE}/api/secondme/friend/break-ice
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| friendId | string | 是 | 好友用户 ID（来自好友列表的 friendId 字段） |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/friend/break-ice" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "friendId": "friend_001"
  }'
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": "sess_67890"
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| data | string | 会话 ID，用于后续聊天 |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| friend.not_found | 好友关系不存在，需要先发送好友邀请 |

---

## Contents

- [Friend List](#friend-list)
- [Send Friend Invitation](#send-friend-invitation)
- [Handle Friend Invitation](#handle-friend-invitation)
- [Break Ice](#break-ice)

## Friend List

When presenting the friend list, show name, latest message, and unread count. Build homepage links as `https://second-me.cn/{route}`.

## Send Friend Invitation

Before sending:

- confirm with the user that they want to send the invitation
- if a greeting is appropriate, draft one and show it for confirmation

After success, inform the user that the invitation was sent and the other person needs to accept.

## Handle Friend Invitation

After accepting, the two users become friends and can chat.

## Break Ice

Use break-ice to start a conversation with a friend. This generates an AI-powered opening message to help start the chat.

Prerequisites:

- the target user must already be a friend (two-way relationship)
- if not friends yet, guide the user to send a friend invitation first

After break-ice succeeds, inform the user that the conversation has been started. If they want to continue chatting, remind them about the SecondMe App:

```
https://go.second-me.cn
```
