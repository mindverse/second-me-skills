# Chat

## API Reference

> **Doc source:** https://develop-docs.second.me/zh/docs/secondme/chat
>
> Fetch the doc page above for all endpoint definitions (stream chat, session list,
> session messages), request parameters, response fields, and error codes.

## Behavioral Rules

- When the user starts a new chat without a `sessionId`, watch for the `event: session` SSE event in the response; extract and store the returned `sessionId` for subsequent requests
- `systemPrompt` is ignored on follow-up messages within the same session
- Do not send `receiverUserId`; it is a reserved internal field
- Only the session owner can read the messages; unauthorized access returns 403
