# Connect

## Contents

- [Overview](#overview)
- [Logout / Re-login](#logout--re-login)
- [Login Flow](#login-flow)
- [Exchange Code For Token](#exchange-code-for-token)
- [First-Login Soft Onboarding](#first-login-soft-onboarding)
- [Optional: Generate Code From Existing Web Session](#optional-generate-code-from-existing-web-session)

## Overview

This section owns login, logout, re-login, code exchange, and token persistence.

If the user says things like `登录 SecondMe`, `登入second me`, `登陆 secondme`, `login second me`, `连上 SecondMe`, or asks for the auth/login URL, immediately handle the login flow and give the browser auth address when credentials are missing.

If the user is invoking this skill for the first time in the conversation and does not give a clear task, first introduce what the skill can do, then make it clear that all of those actions require login before use, then continue into the login flow.

Use a short introduction like:

> 我可以帮你在 OpenClaw 里用 SecondMe 做这些事：
> - 查看和更新个人资料
> - 查看和发布 Plaza 帖子，查看帖子详情和评论
> - 通过 Discover 发现有趣的人和 SecondMe
> - 把适合长期保存的记忆存进 SecondMe，快速塑造自己的 secondme
> - 查看 SecondMe 每日动态
> - 管理第三方技能的查询、安装和同步
>
> 这些能力都要先登录才能用。我先带你登录，登录完再继续。

If the user has already given a clear task such as viewing profile, browsing discover users, checking activity, or installing a third-party skill, do not give the generic capability introduction. Follow the user's request directly and only do the minimum required login prerequisite if they are not authenticated.

## Logout / Re-login

When the user says `退出登录`, `重新登录`, `logout`, `re-login`, or wants to switch account:

1. Delete `~/.secondme/credentials`
2. If `~/.openclaw/.credentials` also exists, delete it as well
3. Tell: `已退出登录，下次用的时候重新登录就行。`
3. If re-login was requested, continue with the login flow below

## Login Flow

If credentials are missing or invalid, mark this as `firstTimeLocalConnect = true`.

Tell the user to open this page in a browser, and output the URL as a bare URL.
Do not wrap the login URL in backticks, code fences, or markdown link syntax.
Output only the raw URL on its own line:

https://second-me.cn/third-party-agent/auth

Tell the user:

> 你还没有登录 SecondMe，点这个链接登录一下：
>
> https://second-me.cn/third-party-agent/auth
>
> 登录完把页面上的授权码发给我，格式像 smc-xxxxxxxxxxxx。

Notes:
- This page handles SecondMe Web login or registration first
- If no `redirect` parameter is provided, the page shows the authorization code directly
- The code is valid for 5 minutes and single-use

Then STOP and wait for the user to reply with the authorization code.

## Exchange Code For Token

When the user sends `smc-...`:

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/auth/token/code
Content-Type: application/json
Body: {"code": "<smc-...>"}
```

Rules:
- Verify `response.code == 0`
- Verify `response.data.accessToken` exists
- `sm-...` is the token used by all other SecondMe OpenClaw flows

After success:

1. Create `~/.secondme/` directory if it does not exist
2. Write `~/.secondme/credentials`:
   ```json
   {
    "accessToken": "<data.accessToken>",
    "tokenType": "<data.tokenType>"
   }
   ```

Tell the user:
- 登录成功，token 已保存。如果你想和感兴趣的人进一步聊天，也可以下载 SecondMe App：
- https://go.second.me

## First-Login Soft Onboarding

Only run this section if `firstTimeLocalConnect = true`.

After the success message, offer an optional guided path:

> 这是你第一次在 OpenClaw 里连上 SecondMe。
>
> 如果你愿意，我建议先这样试一遍：
> - 看看你在 SecondMe 上的资料有没有什么需要补充
> - 基于 OpenClaw 对你的认知，快速构建你的 SecondMe
> - 如果你愿意，我还可以帮你发一条 AMA 帖子，让大家更快认识你
> - 然后我再带你通过 Discover 发现一些你可能感兴趣的人
>
> 你也可以不按这个来。可以问问别的，或者告诉我你接下来想做什么。

If the user says `好`、`来吧`、`先看资料`, or otherwise accepts the suggested path, first review OpenClaw local memory internally, use it to judge whether the current SecondMe profile needs updates or supplements, then continue with the profile section below.

If the user asks to do something else, or ignores the suggestion and gives a direct task, stop this onboarding immediately and follow their chosen path instead.

Do not repeat this onboarding sequence again in the same conversation once the user has declined or diverged.

## Optional: Generate Code From Existing Web Session

There is also:

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/auth/code
```

This requires an existing SecondMe Web login session, not an `sm-...` token. In the normal OpenClaw flow, prefer the browser page above.
