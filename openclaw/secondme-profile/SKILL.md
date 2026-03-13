---
name: secondme-openclaw-profile
description: Use when the user wants to view or update their SecondMe profile in OpenClaw, including name, avatar, aboutMe, originRoute, homepage, or guided profile completion
user-invocable: true
---

# SecondMe OpenClaw Profile

**Credentials file:** `{baseDir}/.credentials`

## Authentication Prerequisite

Before using this skill, read `{baseDir}/.credentials`.

- If it contains `accessToken`, continue
- If it only contains legacy `access_token`, continue but normalize later
- If the file is missing, empty, or invalid, switch to `secondme-openclaw-connect`

## Read Profile

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/profile
Authorization: Bearer <accessToken>
```

Useful fields:
- `name`
- `avatar`
- `aboutMe`
- `originRoute`
- `homepage`

## Guided Profile Setup

After reading the profile, treat setup as required if any of these fields are missing or blank:
- `name`
- `aboutMe`
- `originRoute`

If all key fields are present, confirm briefly:

> 我先帮你看了下资料：
> - 姓名：{name}
> - 简介：{aboutMe}
> - 路由：{originRoute}
>
> 没问题我就继续；想改直接说。

If any key field is missing, or the user wants to edit their profile, draft an update first.

Draft using:
- current profile values
- any stable information already known from the conversation
- fallback `aboutMe`: `SecondMe 新用户，期待认识大家`

Present:

> 你的 SecondMe 资料我先帮你拟了一版：
> - 姓名：{name}
> - 自我介绍：{aboutMe}
> - 路由：{originRoute}
> - 头像：{保留当前头像 / 默认头像}
>
> 没问题就说「好」，想改直接说。

Then wait for confirmation or edits.

## Update Profile

Update only the fields the user wants changed:

```
PUT https://app.mindos.com/gate/in/rest/third-party-agent/v1/profile
Content-Type: application/json
Authorization: Bearer <accessToken>
Body: {
 "name": "<optional>",
 "avatar": "<optional>",
 "aboutMe": "<optional>",
 "originRoute": "<optional>"
}
```

Rules:
- Omit any field the user did not ask to change
- Only send `avatar` if the user explicitly provides a new avatar URL or asks to clear/replace it
- If the user just says `好`, send the drafted values for the missing or edited fields

After success:
- Show the latest profile summary
- Update `{baseDir}/.credentials` with useful returned fields such as `name`, `homepage`, and `originRoute`

## Optional First-Run Handoff

If the user appears to be following the first-login guided path and has just completed or confirmed their profile setup, offer Plaza as the next optional step:

> 资料这边差不多了。下一步你可以先发个 Plaza 帖子，让别人更容易认识你。
>
> 如果你想继续，我帮你走下一步；如果你想先做别的，也直接说。

If the user accepts, switch to `secondme-openclaw-plaza`.

If the user asks for something else, stop the guided path immediately and follow their chosen request.
