# Open APIs for Third-Party Developers

## Contents

- [Agent Memory](#agent-memory)
- [Act (Structured Action)](#act-structured-action)

## Agent Memory

Third-party apps can ingest and query Agent Memory events on behalf of the authenticated user. These events feed into the CTA (Call-To-Action) orchestrator and build the user's activity graph.

### Ingest Event

```
POST {BASE}/api/secondme/agent_memory/ingest
Content-Type: application/json
Authorization: Bearer <accessToken>
Body: {
 "channel": {
   "kind": "<required, e.g. thread/post/comment>",
   "platform": "<optional, defaults to app_id>",
   "id": "<optional>",
   "url": "<optional>",
   "meta": {}
 },
 "action": "<required, e.g. post/reply/operate>",
 "refs": [
   {
     "objectType": "<required, e.g. thread_reply>",
     "objectId": "<required>",
     "type": "external_action",
     "platform": "<optional, inherits channel.platform>",
     "url": "<optional>",
     "contentPreview": "<optional>",
     "snapshot": {
       "text": "<required if snapshot present>",
       "capturedAt": null,
       "hash": null
     }
   }
 ],
 "eventTime": null,
 "signalType": "<optional, e.g. PLAZA_FIND_PEOPLE>",
 "semanticType": "<optional, e.g. PEOPLE_OPPORTUNITY>",
 "entityKey": "<optional, dedup key e.g. plaza_find_people:postId:userId>",
 "ctaEligible": null,
 "actionLabel": "<optional, display text>",
 "eventDesc": "<optional, developer note>",
 "displayText": "<optional, user-readable summary>",
 "idempotencyKey": "<optional>",
 "importance": null,
 "payload": {}
}
```

Rules:

- `userId` is extracted from the auth token automatically; do not include it in the request body
- `channel` and `action` are required; `refs` must contain at least one item
- `channel.platform` defaults to the resolved `app_id` if omitted
- `eventTime` is in milliseconds; defaults to server time if omitted
- `idempotencyKey` prevents duplicate ingestion; generate one using `sha256("external:" + platform + ":" + objectType + ":" + objectId + ":" + userId)` if not provided
- `importance` is a float between 0.0 and 1.0

Response fields:

- `eventId` — the created event ID; `0` means duplicate or invalid
- `isDuplicate` — `true` if `eventId` is `0`

Errors:

- 403 `agent.memory.write.disabled`: user has disabled agent memory writing
- 502 `agent_memory.ingest.failed`: both primary (os-main) and fallback (base-datahub) ingestion failed

### List Events

```
GET {BASE}/api/secondme/agent_memory/list?pageNo=1&pageSize=20&platform=<optional>
Authorization: Bearer <accessToken>
```

Query params:

- `pageNo` (optional, default 1): page number, must be >= 1
- `pageSize` (optional, default 20): items per page, range 1-100
- `platform` (optional): filter by platform

Response fields:

- `items[]` — list of event objects containing `eventId`, `userId`, `eventTime`, `channel`, `action`, `signalType`, `semanticType`, and other fields from the ingest request

Errors:

- 502 `agent_memory.list.failed`: query failed

## Act (Structured Action)

The Act endpoint instructs the user's SecondMe to output a structured JSON judgment instead of freeform text. Use it when your app needs a machine-readable decision from the AI.

### Act Stream

```
POST {BASE}/api/secondme/act/stream
Content-Type: application/json
Authorization: Bearer <accessToken>
Body: {
 "message": "<required>",
 "actionControl": "<required, 20-8000 chars>",
 "sessionId": "<optional>",
 "model": "<optional>",
 "systemPrompt": "<optional>",
 "maxTokens": null
}
```

Request fields:

- `message` (required): the user message or context to judge
- `actionControl` (required): control instructions that define the expected JSON output structure and judgment rules; must be 20-8000 characters and must contain JSON braces `{}`
- `sessionId` (optional): session ID; if omitted the server creates a new session
- `model` (optional): LLM model; same allowed values as Chat stream
- `systemPrompt` (optional): only persisted on the first request of a session
- `maxTokens` (optional): range 1-16000, default 2000

`actionControl` must include:

1. Output format constraint (JSON only, no explanations)
2. JSON field structure example with braces
3. Judgment rules
4. Fallback rules for insufficient evidence

Example `actionControl`:

```
仅输出合法 JSON 对象，不要解释。
输出结构：{"is_liked": boolean}
当用户明确表达喜欢或支持时 is_liked=true，否则 is_liked=false。
信息不足时返回 {"is_liked": false}。
```

Response: Server-Sent Events stream (`text/event-stream`) containing structured JSON output.

Errors:

- 400 `secondme.act.action_control.empty`: actionControl is empty
- 400 `secondme.act.action_control.too_short`: actionControl is shorter than 20 characters
- 400 `secondme.act.action_control.too_long`: actionControl exceeds 8000 characters
- 400 `secondme.act.action_control.invalid_format`: missing JSON structure in actionControl; response includes `issues` array and `suggestions` array
- 403 `auth.scope.missing`: missing `chat` scope
- 403 `secondme.app.banned`: application is banned

Rules:

- Do not send `receiverUserId`; it is a reserved internal field
- Use JSON boolean `true`/`false`, not string `"True"`/`"False"` in actionControl examples
- The response error object includes `constraints`, `issues`, and `suggestions` fields to help fix invalid actionControl
