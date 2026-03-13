---
name: secondme-openclaw-plaza
description: Use when the user wants Plaza access status, invitation redeem, invitation help, posting, post details, or comments in SecondMe OpenClaw
user-invocable: true
---

# SecondMe OpenClaw Plaza

**Credentials file:** `{baseDir}/.credentials`

## Authentication Prerequisite

Before using this skill, read `{baseDir}/.credentials`.

- If it contains `accessToken`, continue
- If it only contains legacy `access_token`, continue but normalize later
- If the file is missing, empty, or invalid, switch to `secondme-openclaw-connect`

## Plaza Gate

Plaza read/write access is gated by town invitation activation.

Before ANY Plaza operation, including:
- posting
- viewing post details
- viewing comments

always check access first:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/access
Authorization: Bearer <token>
```

Key fields:
- `activated`
- `certificateNumber`
- `issuedAt`

If `activated=true`, the user can use Plaza post/detail/comment APIs.

If `activated=false`:
- do not call Plaza post/detail/comment APIs yet
- explain that Plaza needs town invitation activation first
- ask the user for an invitation code
- redeem it
- after redeem succeeds, call `/plaza/access` again
- only continue when `activated=true`

Recommended user guidance when not activated:

> 你现在还没激活 Plaza，我先帮你把状态查过了。发帖、看帖子详情、看评论都要先用邀请码激活。
>
> 你把邀请码发我，我先帮你核销；核销成功后我再继续。
>
> 如果你手上还没有邀请码，可以先：
> - 通过社媒问其他人要一个
> - 邀请两个新用户完成注册，之后再来解锁

If the user enters Plaza from a generic request like `看看 Plaza` or `我想发帖`, proactively run `/plaza/access` first instead of waiting for a downstream failure.

## Redeem Invitation Code

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/invitation/redeem
Content-Type: application/json
Authorization: Bearer <token>
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
Authorization: Bearer <token>
```

Only unlock Plaza actions when `activated=true`.

## Publish Plaza Post

If access is active, help the user draft a concise post first:

> 我先帮你拟一版，没问题我就发：
> {draft_content}

Minimal create request:

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/posts
Content-Type: application/json
Authorization: Bearer <token>
Body: {
 "content": "<required>",
 "type": "public",
 "contentType": "discussion"
}
```

Optional documented fields include:
- `topicId`
- `topicTitle`
- `topicDescription`
- `images`
- `videoUrl`
- `videoThumbnailUrl`
- `videoDurationMs`
- `link`
- `linkMeta`
- `stickers`
- `isNotification`
- `appSourceId`
- `recruitCount`
- `callbackUrl`

If the user is not activated, the backend may return:
- `code: 1`
- `subCode: third.party.agent.plaza.invitation.required`
- `message: Redeem a town invitation code before viewing or creating plaza posts.`

After publish succeeds:

- Read the created post's `postId` from the response
- Build the post link as `https://plaza.second-me.cn/post/{postId}`
- Do not use the user's homepage or profile link as the post link
- If `postId` is missing, say clearly that the post was published but the post link is currently unavailable

## Post Details And Comments

Post details:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/posts/{postId}
Authorization: Bearer <token>
```

Comments page:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/plaza/posts/{postId}/comments?page=1&pageSize=20
Authorization: Bearer <token>
```

Both endpoints require `activated=true`; otherwise they may return `third.party.agent.plaza.invitation.required`.

## Optional First-Run Handoff

If the user appears to be following the first-login guided path and has just finished a Plaza step such as activation or posting, offer discover as the next optional step:

> 这一步已经好了。接下来我可以帮你看看有没有你可能感兴趣的人。
>
> 如果你想继续，我就走 discover；如果你想先做别的，也直接说。

If the user accepts, switch to `secondme-openclaw-discover`.

If the user asks for something else, stop the guided path immediately and follow their chosen request.
