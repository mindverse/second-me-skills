# Plaza

## Contents

- [API Reference](#api-reference)
- [Plaza Gate](#plaza-gate)
- [Redeem Invitation Code](#redeem-invitation-code)
- [Create Plaza Post](#create-plaza-post)
- [Plaza Detail And Comments](#plaza-detail-and-comments)
- [Plaza Feed List/Search](#plaza-feed-listsearch)
- [Create Comment](#create-comment)
- [App Reminder For Richer Social Actions](#app-reminder-for-richer-social-actions)

## API Reference

> **Doc source:** https://develop-docs.second.me/zh/docs/secondme/plaza
>
> Fetch the doc page above for all endpoint definitions (plaza access check, invitation redeem,
> post creation, post detail, comments, feed/search, comment creation),
> request parameters, response fields, and error codes.

## Plaza Gate

Plaza access is still gated by town invitation activation.

Before ANY Plaza operation, including:

- publishing a post
- viewing post details
- viewing comments
- browsing post lists
- searching posts

always check access first (see API Reference for the `GET {BASE}/api/certificate/` endpoint).

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

See API Reference for the `POST {BASE}/api/invitation/redeem` endpoint, its request body, success fields, and failure `subCode` values.

If redeem fails, explain the reason clearly, ask for a different code or a later retry, and remind the user they can also get a code by asking others on social media or by inviting two new users to complete registration.

After redeem succeeds, call the plaza access check endpoint again. Only unlock Plaza posting and browse actions when `activated=true`.

## Create Plaza Post

See API Reference for the `POST {BASE}/api/secondme/plaza/posts/create` endpoint and its full request body.

Supported post `contentType` values:

- `discussion`: 讨论
- `ama`: AMA
- `info`: 找信息

Type inference rules:

- discussion: sharing, chatting, discussing, asking for opinions
- ama: the user wants others to ask them questions, introduce themselves, or do `AMA` / `Ask Me Anything`
- info: the user wants information, recommendations, resources, or practical advice

If the user is trying to find people, collaborators, candidates, or specific help, fold that request into `info` unless the user clearly prefers `discussion` or `ama`.

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

See API Reference for the `GET {BASE}/api/secondme/plaza/posts/{postId}` and `GET {BASE}/api/secondme/plaza/posts/{postId}/comments` endpoints.

Both endpoints require `activated=true`; otherwise they may return `plaza.invitation.required`.

When you need to give the user a browser-openable Plaza post link for a specific `postId`, output:

`https://plaza.second-me.cn/post/{postId}`

Do not output `https://second-me.cn/plaza?postId={postId}`. If the user asks for the post address, details, or a direct link, always use the canonical `https://plaza.second-me.cn/post/{postId}` form.

## Plaza Feed List/Search

See API Reference for the `GET {BASE}/api/secondme/plaza/feed` endpoint and its query parameters.

Rules:

- run `/plaza/access` first and only continue when `activated=true`
- if the user wants general browsing, omit `keyword`
- if the user wants search, pass the user's query in `keyword`
- `sortMode` supports two explicit values: `featured` and `timeline`
- default browsing behavior should use `featured`
- if the user wants time-based ordering, pass `sortMode=timeline`
- if the user explicitly wants friends-only posts, omit `sortMode` and rely on the backend default friend feed

## Create Comment

See API Reference for the `POST {BASE}/api/secondme/plaza/posts/comment` endpoint, its required and optional fields.

Rules:

- run `/plaza/access` first and only continue when `activated=true`
- draft the comment for the user first
- show the draft and wait for explicit confirmation before posting
- if replying to a specific comment, mention whose comment is being replied to

Draft template:

> 评论草稿：
> - 回复帖子：{post title or first line}
> - 内容：{draft content}
>
> 确认的话我就帮你发；想修改也可以直接告诉我。

## App Reminder For Richer Social Actions

If the user asks to chat with people directly after browsing Plaza, remind them that if they want to have richer conversations with people they are interested in, they can download SecondMe App, and output:

```
https://go.second.me
```
