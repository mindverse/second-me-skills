# Friend

## Contents

- [Friend List](#friend-list)
- [Send Friend Invitation](#send-friend-invitation)
- [Handle Friend Invitation](#handle-friend-invitation)
- [Break Ice](#break-ice)

## Friend List

```
GET {BASE}/api/secondme/friend/list
Authorization: Bearer <accessToken>
```

Query params:

- `type` — default `FRIEND`
- `pageNo` — default `1`
- `pageSize` — default `20`, max `100`

Key response fields:

- `friends` — array of friend objects, each containing:
  - `friendId` — encoded friend user ID
  - `name` — display name
  - `avatar` — avatar URL
  - `sessionId` — DM session ID
  - `relationType` — e.g., `two-way-friend`
  - `latestMessage` — last message preview
  - `latestMessageTime` — timestamp (ms)
  - `unreadCount`
  - `route` — user homepage route
  - `source` — how they became friends
- `total` — total friend count
- `friendInvitation` — pending invitation summary
- `totalUnreadCount`

When presenting the friend list, show name, latest message, and unread count. Build homepage links as `https://second-me.cn/{route}`.

## Send Friend Invitation

```
POST {BASE}/api/secondme/friend/invite/send
Content-Type: application/json
Authorization: Bearer <accessToken>
Body: {
  "targetUserId": "<user id>",
  "greeting": "<optional greeting message>",
  "source": "<optional source identifier>",
  "sourceData": { "<optional key>": "<value>" }
}
```

Required fields:

- `targetUserId` — the user to invite (max 50 chars)

Optional fields:

- `greeting` — greeting message (max 500 chars)
- `source` — where the user found this person (e.g., `DISCOVER`, `PLAZA`)
- `sourceData` — additional source context

Before sending:

- confirm with the user that they want to send the invitation
- if a greeting is appropriate, draft one and show it for confirmation

After success, inform the user that the invitation was sent and the other person needs to accept.

## Handle Friend Invitation

```
POST {BASE}/api/secondme/friend/invite/handle
Content-Type: application/json
Authorization: Bearer <accessToken>
Body: {
  "targetUserId": "<user id who sent the invitation>",
  "action": "ACCEPTED" | "REJECTED"
}
```

Required fields:

- `targetUserId` — the user who sent the invitation
- `action` — must be exactly `ACCEPTED` or `REJECTED`

After accepting, the two users become friends and can chat.

## Break Ice

Use break-ice to start a conversation with a friend. This generates an AI-powered opening message to help start the chat.

```
POST {BASE}/api/secondme/friend/break-ice
Content-Type: application/json
Authorization: Bearer <accessToken>
Body: {
  "friendId": "<friend user id>"
}
```

Required fields:

- `friendId` — the friend's user ID (from the friend list `friendId` field)

Returns:

- `data` — the session ID for the newly created or existing conversation

Prerequisites:

- the target user must already be a friend (two-way relationship)
- if not friends yet, guide the user to send a friend invitation first

After break-ice succeeds, inform the user that the conversation has been started. If they want to continue chatting, remind them about the SecondMe App:

```
https://go.second.me
```
