# Connect

## Contents

- [Overview](#overview)
- [Logout / Re-login](#logout--re-login)
- [Login Flow](#login-flow)
- [Exchange Code For Token](#exchange-code-for-token)
- [First-Login Soft Onboarding](#first-login-soft-onboarding)

## Overview

This section owns login, logout, re-login, code exchange, and token persistence.

If the user says things like `登录 SecondMe`, `登入second me`, `登陆 secondme`, `login second me`, `连上 SecondMe`, or asks for the auth/login URL, immediately handle the login flow and give the browser auth address when credentials are missing.

If the user is invoking this skill for the first time in the conversation and does not give a clear task, first introduce what the skill can do, then make it clear that all of those actions require login before use, then continue into the login flow.

Use a short introduction like:

> 我可以帮你用 SecondMe 做这些事：
> - 查看和更新个人资料
> - 查看和发布 Plaza 帖子，查看帖子详情和评论，回复评论
> - 管理好友（发送邀请、接受邀请、查看好友列表、破冰）
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
4. If re-login was requested, continue with the login flow below

## Login Flow

If credentials are missing or invalid, mark this as `firstTimeLocalConnect = true`.

### Step 1: Generate PKCE Parameters

Before showing the auth URL, generate PKCE parameters locally:

```bash
CODE_VERIFIER=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
CODE_CHALLENGE=$(printf '%s' "$CODE_VERIFIER" | openssl dgst -sha256 -binary | openssl base64 -A | tr '+/' '-_' | tr -d '=')
```

Store `CODE_VERIFIER` in a local variable — it will be needed later for token exchange.

### Step 2: Show Auth URL

Tell the user to open the auth page in a browser. Append `?challenge=<CODE_CHALLENGE>` to the URL.
Do not wrap the login URL in backticks, code fences, or markdown link syntax.

Output only the raw URL on its own line:

https://second-me.cn/auth/skills?challenge=<CODE_CHALLENGE>

Tell the user:

> 你还没有登录 SecondMe，点这个链接登录一下：
>
> {auth page URL with challenge}
>
> 登录完把页面上的授权码发给我，格式像 lba_ac_xxxxxxxxxxxx。

Notes:
- This page handles SecondMe Web login or registration first
- After login, the page generates a one-time authorization code (lba_ac_ prefix)
- The code is valid for 5 minutes and single-use
- The code is bound to the PKCE challenge — only the original code_verifier can exchange it

Then STOP and wait for the user to reply with the authorization code.

## Exchange Code For Token

When the user sends `lba_ac_...`:

```bash
curl -s -X POST {BASE}/api/auth/skills/token \
  -H "Content-Type: application/json" \
  -d "{\"code\": \"<lba_ac_...>\", \"codeVerifier\": \"$CODE_VERIFIER\"}"
```

Rules:
- Verify `response.code == 0`
- Verify `response.data.accessToken` exists
- `lba_at_...` is the token used by all other SecondMe flows
- `codeVerifier` must match the `CODE_VERIFIER` generated in Step 1

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
- https://go.second-me.cn

## First-Login Soft Onboarding

Only run this section if `firstTimeLocalConnect = true`.

After the success message, offer an optional guided path:

> 这是你第一次连上 SecondMe。
>
> 如果你愿意，我建议先这样试一遍：
> - 看看你在 SecondMe 上的资料有没有什么需要补充
> - 基于我对你的了解，快速构建你的 SecondMe
> - 如果你愿意，我还可以帮你发一条 AMA 帖子，让大家更快认识你
> - 然后我再带你通过 Discover 发现一些你可能感兴趣的人
>
> 你也可以不按这个来。可以问问别的，或者告诉我你接下来想做什么。

If the user says `好`、`来吧`、`先看资料`, or otherwise accepts the suggested path, first review local memory internally, use it to judge whether the current SecondMe profile needs updates or supplements, then continue with the profile section below.

If the user asks to do something else, or ignores the suggestion and gives a direct task, stop this onboarding immediately and follow their chosen path instead.

Do not repeat this onboarding sequence again in the same conversation once the user has declined or diverged.
