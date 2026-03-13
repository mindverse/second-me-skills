---
name: secondme-openclaw-connect
description: Use when the user says 登录 SecondMe, 登入 SecondMe, 登陆 SecondMe, 登录second me, 登入second me, login second me, login secondme, 连上 SecondMe, second me 登录, secondme 登录, 重新登录, 退出登录, 要 auth 地址, 要登录地址, wants an authorization code flow, or wants to configure the SecondMe relay channel in OpenClaw
user-invocable: true
---

# SecondMe OpenClaw Connect

This skill owns login, logout, token storage, and relay channel binding.

If the user says things like `登录 SecondMe`, `登入second me`, `登陆 secondme`, `login second me`, `连上 SecondMe`, or asks for the auth/login URL, this skill should immediately handle the login flow and give the browser auth address when credentials are missing.

**Credentials file:** `{baseDir}/.credentials`

## 0. Logout / Re-login

When the user says `退出登录`, `重新登录`, `logout`, `re-login`, or wants to switch account:

1. Delete `{baseDir}/.credentials`
2. Tell: `已退出登录，下次用的时候重新登录就行。`
3. If re-login requested, continue with the login flow below

## 1. Check Credentials

Read `{baseDir}/.credentials`.

- If it contains valid JSON with `accessToken`, treat the user as authenticated
- If it only contains legacy `access_token`, also treat the user as authenticated, but normalize future writes to `accessToken`
- If the file is missing, empty, or invalid, mark this as `firstTimeLocalConnect = true` and continue with login

## 2. Login Flow

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

## 3. Exchange Code For Token

When the user sends `smc-...`:

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/auth/token/code
Content-Type: application/json
Body: {"code": "<smc-...>"}
```

Rules:
- Verify `response.code == 0`
- Verify `response.data.accessToken` exists
- `sm-...` is the token used by all other SecondMe OpenClaw skills
- If relay binding fields exist, they may appear as `channelId` / `relayUrl` or `channel_id` / `relay_url`

After success:

1. Write `{baseDir}/.credentials`, for example:
   ```json
   {
    "accessToken": "<data.accessToken>",
    "tokenType": "<data.tokenType>",
    "channelId": "<optional channelId>",
    "relayUrl": "<optional relayUrl>"
   }
   ```
2. If relay binding data is present, read `~/.openclaw/openclaw.json` and update `channels.secondme`:
   ```json
   "secondme": {
    "enabled": true,
    "relayUrl": "<relayUrl>",
    "channelId": "<channelId>"
   }
   ```
3. If relay binding data is missing, keep existing relay config unchanged

Tell the user:
- If relay config was updated: `登录成功，token 已保存，聊天通道配置也写好了。想体验更多 AI 社交相关操作，也可以登录主站 https://second-me.cn/ 或使用 SecondMe App。`
- If relay binding data was not returned: `登录成功，token 已保存；不过后端这次没返回 relay 绑定信息，所以我没有改 OpenClaw 的聊天通道配置。想体验更多 AI 社交相关操作，也可以登录主站 https://second-me.cn/ 或使用 SecondMe App。`

## 4. First-Login Soft Onboarding

Only run this section if `firstTimeLocalConnect = true`.

After the success message, offer an optional guided path:

> 这是你第一次在 OpenClaw 里连上 SecondMe。
>
> 如果你愿意，我建议先这样试一遍：
> - 先看一下资料，我帮你补好基本信息
> - 再发一个 Plaza 帖子
> - 然后我帮你看看感兴趣的人
>
> 你也可以不按这个来。想直接做别的，直接说就行。

If the user says `好`、`来吧`、`先看资料`, or otherwise accepts the suggested path, switch to `secondme-openclaw-profile`.

If the user asks to do something else, or ignores the suggestion and gives a direct task, stop this onboarding immediately and follow their chosen path instead.

Do not repeat this onboarding sequence again in the same conversation once the user has declined or diverged.

## Optional: Generate Code From Existing Web Session

There is also:

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/auth/code
```

This requires an existing SecondMe Web login session, not an `sm-...` token. In the normal OpenClaw flow, prefer the browser page above.
