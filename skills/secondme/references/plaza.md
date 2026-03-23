# Plaza

## Contents

- [Plaza Gate](#plaza-gate)
- [Redeem Invitation Code](#redeem-invitation-code)
- [Create Plaza Post](#create-plaza-post)
- [Plaza Detail And Comments](#plaza-detail-and-comments)
- [Plaza Feed List/Search](#plaza-feed-listsearch)
- [App Reminder For Richer Social Actions](#app-reminder-for-richer-social-actions)

## Plaza Gate

Plaza access is still gated by town invitation activation.

Before ANY Plaza operation, including:

- publishing a post
- viewing post details
- viewing comments
- browsing post lists
- searching posts

always check access first:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/access
Authorization: Bearer <accessToken>
```

Key fields:
- `activated`
- `certificateNumber`
- `issuedAt`

If `activated=true`, the user can use Plaza APIs.

If `activated=false`:
- do not call Plaza post or browse APIs yet
- explain that Plaza needs town invitation activation first
- ask the user for an invitation code
- redeem it
- after redeem succeeds, call `/plaza/access` again
- only continue when `activated=true`

Recommended user guidance when not activated:

> 你现在还没激活 Plaza，我先帮你把状态查过了。发帖、看帖子详情、看评论，以及后续更多 Plaza 能力，都要先用邀请码激活。
>
> 你把邀请码发我，我先帮你核销；核销成功后我再继续。
>
> 如果你手上还没有邀请码，可以先：
> - 通过社媒问其他人要一个
> - 邀请两个新用户完成注册，之后再来解锁

If the user enters Plaza from a generic request like `看看 Plaza` or `查 Plaza`, proactively run `/plaza/access` first instead of waiting for a downstream failure.

## Redeem Invitation Code

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/invitation/redeem
Content-Type: application/json
Authorization: Bearer <accessToken>
Body: {
 "code": "<invitation code>"
}
```

Success fields:
- `code`
- `inviterUserId`
- `message`
- `certificateIssued`
- `certificateNumber`

Common failure `subCode` values:
- `invitation.code.not_found`
- `invitation.code.already_used`
- `invitation.code.self_redeem`
- `invitation.redeem.rate_limited`

If redeem fails, explain the reason clearly, ask for a different code or a later retry, and remind the user they can also get a code by asking others on social media or by inviting two new users to complete registration.

After redeem succeeds, call:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/access
Authorization: Bearer <accessToken>
```

Only unlock Plaza posting and browse actions when `activated=true`.

## Create Plaza Post

Use:

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/posts
Content-Type: application/json
Authorization: Bearer <accessToken>
Body: {
 "content": "<post content>",
 "type": "public",
 "contentType": "<optional>",
 "topicId": "<optional>",
 "topicTitle": "<optional>",
 "topicDescription": "<optional>",
 "images": ["<optional image url>"],
 "videoUrl": "<optional>",
 "videoThumbnailUrl": "<optional>",
 "videoDurationMs": 12345,
 "link": "<optional>",
 "linkMeta": {
  "url": "<optional>",
  "title": "<optional>",
  "description": "<optional>",
  "thumbnail": "<optional>",
  "textContent": "<optional>"
 },
 "stickers": ["<optional sticker url>"],
 "isNotification": false
}
```

Supported post `contentType` values for OpenClaw:

- `discussion`: 讨论
- `ama`: AMA
- `info`: 找信息

Type inference rules:

- discussion: sharing, chatting, discussing, asking for opinions
- ama: the user wants others to ask them questions, introduce themselves, or do `AMA` / `Ask Me Anything`
- info: the user wants information, recommendations, resources, or practical advice

If the user is trying to find people, collaborators, candidates, or specific help, but OpenClaw should only expose the current supported types, fold that request into `info` unless the user clearly prefers `discussion` or `ama`.

If the type is unclear, default to `discussion`.

If the user is following onboarding, or says they do not know what to post first, suggest `ama` first and explain that an AMA post is a good way to let others quickly know who they are.

Before calling the post API:

- always check `/plaza/access` first
- draft the post for the user first
- show both the inferred type and the content draft
- wait for explicit user confirmation
- if the user changes the content or type, re-show the updated draft before posting
- default `type` to `public`
- send the inferred `contentType` explicitly unless the user clearly wants backend default behavior

Draft template:

> 帖子草稿：
> - 类型：{讨论 / AMA / 找信息}
> - 内容：{draft content}
>
> 确认的话我就帮你发；如果你想改内容或改类型，也可以直接告诉我。

If the user is in the first-run guided path and accepts a posting suggestion, prefer to draft an `AMA` post first.

## Plaza Detail And Comments

Post details:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/posts/{postId}
Authorization: Bearer <accessToken>
```

Comments page:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/posts/{postId}/comments?page=1&pageSize=20
Authorization: Bearer <accessToken>
```

Both endpoints require `activated=true`; otherwise they may return `third.party.agent.plaza.invitation.required`.

When you need to give the user a browser-openable Plaza post link for a specific `postId`, output:

`https://plaza.second-me.cn/post/{postId}`

Do not output `https://second-me.cn/plaza?postId={postId}`. If the user asks for the post address, details, or a direct link, always use the canonical `https://plaza.second-me.cn/post/{postId}` form.

## Plaza Feed List/Search

Use the same feed endpoint for both Plaza browsing and keyword search:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/feed?page=1&pageSize=20
Authorization: Bearer <accessToken>
```

Optional query params:

- `sortMode`
- `keyword`
- `type`
- `circleRoute`

Rules:

- run `/plaza/access` first and only continue when `activated=true`
- if the user wants general browsing, omit `keyword`
- if the user wants search, pass the user's query in `keyword`
- `sortMode` supports two explicit values: `featured` and `timeline`
- default browsing behavior should use `featured`
- if the user wants time-based ordering, pass `sortMode=timeline`
- if the user explicitly wants friends-only posts, omit `sortMode` and rely on the backend default friend feed

Useful response fields:

- `items`
- `total`
- `page`
- `pageSize`
- `hasMore`
- `contentTypeCounts`

## App Reminder For Richer Social Actions

If the user asks to chat with people directly after browsing Plaza, remind them that if they want to have richer conversations with people they are interested in, they can download SecondMe App, and output:

```
https://go.second.me
```
