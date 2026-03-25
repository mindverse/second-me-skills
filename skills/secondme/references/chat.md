# Chat

## Contents

- [Stream Chat](#stream-chat)
- [Session List](#session-list)
- [Session Messages](#session-messages)

## Stream Chat

```
POST {BASE}/api/secondme/chat/stream
Content-Type: application/json
Authorization: Bearer <accessToken>
Body: {
 "message": "<required>",
 "sessionId": "<optional>",
 "model": "<optional>",
 "systemPrompt": "<optional>",
 "enableWebSearch": false,
 "images": [],
 "maxTokens": null
}
```

Request fields:

- `message` (required): user message content
- `sessionId` (optional): session ID; if omitted the server creates a new session and injects a `session` SSE event containing the new `sessionId`
- `model` (optional): LLM model; allowed values include `anthropic/claude-sonnet-4-5`, `cloudsway/claude-sonnet-4.6`, `google_ai_studio/gemini-2.0-flash`; default is chosen by the server
- `systemPrompt` (optional): system prompt, only persisted on the first request of a session
- `enableWebSearch` (optional, default `false`): enable web search augmentation
- `images` (optional): base64-encoded image list, max 4 items; each item has `data` (base64 without `data:` prefix) and `mediaType` (`image/png`, `image/jpeg`, `image/gif`, or `image/webp`)
- `maxTokens` (optional): max output tokens, range 1-16000, default 2000

Response: Server-Sent Events stream (`text/event-stream`).

Rules:

- When the user starts a new chat without a `sessionId`, watch for the `event: session` SSE event in the response; extract and store the returned `sessionId` for subsequent requests
- `systemPrompt` is ignored on follow-up messages within the same session
- Do not send `receiverUserId`; it is a reserved internal field

Errors:

- 403 `auth.scope.missing`: missing `chat` scope
- 403 `secondme.app.banned`: application is banned

## Session List

```
GET {BASE}/api/secondme/chat/session/list?appId=<optional>
Authorization: Bearer <accessToken>
```

Query params:

- `appId` (optional): filter sessions by application ID

Response fields:

- `sessions[]` — list of sessions
  - `sessionId`
  - `appId`
  - `lastMessage` — last message preview (may be null)
  - `lastUpdateTime` — last update timestamp (may be null)
  - `messageCount`

## Session Messages

```
GET {BASE}/api/secondme/chat/session/messages?sessionId=<required>
Authorization: Bearer <accessToken>
```

Query params:

- `sessionId` (required): session ID

Response fields:

- `sessionId`
- `messages[]` — messages in chronological order
  - `messageId`
  - `role` — `system`, `user`, or `assistant`
  - `content`
  - `senderUserId` — encoded user ID
  - `receiverUserId` — encoded user ID or null
  - `createTime`

Rules:

- Only the session owner can read the messages; unauthorized access returns 403 `secondme.session.unauthorized`
