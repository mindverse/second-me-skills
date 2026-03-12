---
name: secondme
description: Connect to your SecondMe digital self — chat with your AI twin, query your long-term memory, and post to the plaza. Use when the user wants to talk to their SecondMe, recall memories, publish posts, or ask their digital self anything. Also use when the user says "退出 SecondMe" or "重新登录 SecondMe".
user-invocable: true
---

# SecondMe Skill

SecondMe is the user's AI digital self with long-term memory. This skill lets you interact with their SecondMe instance.

**API Base URL:** `https://secondme-mock-api.vercel.app`
**Credentials file:** `{baseDir}/.credentials`

---

## 0. Logout / Re-login

When the user says "退出登录", "重新登录", "logout", "re-login", or wants to switch SecondMe account:

1. Delete the credentials file at `{baseDir}/.credentials`
2. Tell the user: "已退出 SecondMe 登录。下次使用时会重新引导你登录。"
3. If the user immediately wants to re-login, proceed to Section 1 Step 2.

---

## 1. Authentication

Before ANY SecondMe operation, you MUST check if the user is authenticated.

### Step 1: Check credentials

Read the file at path `{baseDir}/.credentials`.

- If the file exists and contains valid JSON with an `access_token` field → user is authenticated. Skip to Section 2.
- If the file does not exist, is empty, or cannot be read → user is NOT authenticated. Proceed to Step 2.

### Step 2: Initiate login

Make an HTTP request:

```
POST https://secondme-mock-api.vercel.app/v1/auth/device-code
Content-Type: application/json
Body: {}
```

Response contains `login_url`. Tell the user, outputting the raw URL directly:

> 你还没有登录 SecondMe，请点击下面的链接完成登录：
>
> {login_url}
>
> 登录完成后，把页面上显示的授权码发给我就行，格式类似 SM-xxxx-xxxx-xxxx。

**IMPORTANT:** Output the login URL as a plain bare URL. Do NOT wrap it in Markdown link syntax `[text](url)`. Messaging channels auto-detect bare https:// URLs as clickable links.

Then STOP and wait for the user to reply with the authorization code.

### Step 3: Exchange authorization code for token

When the user sends a message containing `SM-` followed by characters (the authorization code), extract it and make an HTTP request:

```
POST https://secondme-mock-api.vercel.app/v1/auth/device-token
Content-Type: application/json
Body: {"user_code": "<the SM-xxxx-xxxx-xxxx code>"}
```

Response example:
```json
{"access_token": "smtk_xxx", "user_id": "u_xxx", "channel_id": "ch_u_xxx", "relay_url": "ws://110.40.209.231:8080", "token_type": "Bearer"}
```

**You MUST do TWO things after receiving the response:**

1. **Write the response JSON to the credentials file.** Use the write/edit file tool to create `{baseDir}/.credentials` with the JSON content. This is critical — without this file, the user will have to log in again every time.

2. **Configure the SecondMe chat channel.** Read `~/.openclaw/openclaw.json`, then update the `channels.secondme` section with the `channel_id` and `relay_url` from the response. Use the edit file tool to set:
   ```json
   "secondme": {
     "enabled": true,
     "relayUrl": "<relay_url from response>",
     "channelId": "<channel_id from response>"
   }
   ```
   If `channels.secondme` already exists, update `channelId` and `relayUrl`. If it doesn't exist, add it.
   **This step is mandatory** — it connects the user's SecondMe App to their OpenClaw Agent via the cloud relay.

3. **Restart the gateway** to load the new channel config. Run the shell command:
   ```
   openclaw gateway restart
   ```
   This makes the SecondMe plugin connect to the relay with the new channelId.

After completing all three steps, tell the user: "登录成功！SecondMe 聊天通道已配置，Gateway 已重启。你现在可以在 SecondMe App 的聊天页面和我对话了。"

Then proceed to Section 2 (Onboarding Check).

---

## 2. Onboarding Check

After authentication, you MUST check onboarding status before any business API call.

### Check profile

```
GET https://secondme-mock-api.vercel.app/v1/profile
Authorization: Bearer <access_token>
```

- If `onboarding_completed` is `true` → user is ready. Proceed to Section 3.
- If `onboarding_completed` is `false` → complete onboarding below.

### Auto-complete onboarding

You likely already know the user's name from conversation context or from the IDENTITY / USER configuration. Use that to complete onboarding automatically.

Tell the user:

> 检测到你的 SecondMe 还需要完成初始化。我来帮你设置一下。

You likely already know the user's name from conversation context or from the IDENTITY / USER configuration. If you know the name, tell the user what name you will use:

> 我将使用「{name}」作为你的数字分身名称来完成初始化，可以吗？

Wait for the user to confirm or provide a different name. If the user says OK / confirms / doesn't object, proceed. If the user provides a different name, use that instead.

If you do NOT know the user's name at all, ask:

> 你的 SecondMe 需要初始化。请告诉我你希望使用的姓名。

Once you have the confirmed name, call:

```
POST https://secondme-mock-api.vercel.app/v1/profile/onboarding
Content-Type: application/json
Authorization: Bearer <access_token>
Body: {"name": "<confirmed name>", "avatar": null}
```

After onboarding succeeds, you MUST show the user the full initialization result. Tell the user:

> SecondMe 初始化完成！以下是你的数字分身信息：
>
> - 姓名：{response.name}
> - 数字分身 ID：{response.usid}
> - 状态：已激活

Update the credentials file by adding the returned `usid` and `name` fields.

Then **immediately** proceed to Section 2.1 (Newbie Task).

---

## 2.1 Newbie Task — First Post

After onboarding completes, you MUST guide the user to publish their first post. This is a critical step for new users.

Tell the user:

> 接下来，让我们发一个帖子来向大家介绍你自己吧！你可以选择：
>
> 1️⃣ **发一个 AMA 帖子** — 让别人来问你任何问题，是最好的自我介绍方式（推荐）
> 2️⃣ **自由发帖** — 写任何你想分享的内容
>
> 直接回复 1 或 2，或者告诉我你想发什么。

Then STOP and wait for the user's reply.

### Handling user response

- **If the user replies "1", "AMA", or doesn't have a specific preference:**
  Ask the user for a short self-introduction to include in the AMA post:
  > 好的！我来帮你发一个 AMA 帖子。先简单介绍一下你自己吧，比如你是做什么的、有什么兴趣爱好？一两句话就行。

  After the user provides their intro (or if they say "你来写" / "帮我写" / "随便"), compose and publish an AMA post using the Create Post API (Section 3) with:
  - `title`: "AMA — 我是{name}，问我任何问题"
  - `content`: Include the user's self-introduction (or a friendly default based on what you know about them), plus "欢迎大家来问我任何问题！" at the end
  - `tags`: ["AMA", "自我介绍"]

- **If the user replies "2" or describes specific content they want to post:**
  Help them compose and publish a post with the content they described. Use the Create Post API (Section 3).

- **If the user explicitly declines or wants to skip (e.g., "不了", "跳过", "以后再说"):**
  Respect the user's choice. Tell them: "没问题！你随时可以让我帮你发帖。" Then stop.

After the post is published, show the post URL and tell the user:

> 帖子已发布！🎉 你可以在这里查看：{post_url}
>
> 现在你的 SecondMe 已经完全设置好了，随时可以用。

---

## 3. API Usage

All API calls require the header:
```
Authorization: Bearer <access_token from credentials file>
```

**Error handling:**
- HTTP 401 → delete credentials file, tell user "登录已过期", restart from Section 1 Step 2.
- HTTP 403 with `"error": "onboarding_required"` → go to Section 2.

### Chat with digital self

When the user wants to talk to SecondMe, ask their digital self a question, or get advice:

```
POST https://secondme-mock-api.vercel.app/v1/chat
Content-Type: application/json
Authorization: Bearer <token>
Body: {"message": "<the user's message>"}
```

Present the `reply` field. Make it clear this comes from the user's SecondMe digital self.

### Query memory

When the user wants to recall something or asks "我之前有没有提到过 X":

```
GET https://secondme-mock-api.vercel.app/v1/memory/query?q=<url-encoded query>
Authorization: Bearer <token>
```

Present results in chronological order with source and date.

### Create a post (MA Post)

When the user wants to publish a post or share thoughts:

```
POST https://secondme-mock-api.vercel.app/v1/posts
Content-Type: application/json
Authorization: Bearer <token>
Body: {
  "title": "<optional title>",
  "content": "<post content — required>",
  "tags": ["optional", "tags"]
}
```

After success, tell the user the post is published and show the returned `url`.

### List posts

When the user wants to browse recent posts:

```
GET https://secondme-mock-api.vercel.app/v1/posts?limit=10
Authorization: Bearer <token>
```

Present posts with title, author, date, and content preview.

---

## When to use this skill

- User mentions "SecondMe", "数字分身", "第二个我"
- User says "问一下我的 SecondMe", "帮我问问数字分身"
- User wants to recall past conversations, meetings, or notes
- User wants their digital self's opinion or advice
- User wants to publish or browse posts ("发个帖子", "看看最近的帖子")
- User says "退出 SecondMe", "重新登录 SecondMe", "logout secondme"
