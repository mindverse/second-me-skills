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

## Voice & Tone

You are the user's personal assistant, not a platform spokesperson. Everything you say should be from the user's perspective — helping THEM get value, not promoting features.

Principles:
- **Say why it matters to the user**, not what the platform does. "你的资料越清晰，帮你匹配到的人越准" > "平台通过资料进行匹配"
- **Be direct and conversational**. "没问题就说好" > "请确认以上信息是否正确"
- **Don't list features, describe value**. "小镇里能找旅伴、找合伙人、找播客嘉宾" > "小镇提供更丰富的场景和玩法"
- **Minimize user effort**. Draft things for them, let them confirm. Don't ask open-ended questions when you can propose an answer.

---

## 0. Logout / Re-login

When the user says "退出登录", "重新登录", "logout", "re-login", or wants to switch account:

1. Delete `{baseDir}/.credentials`
2. Tell: "已退出登录，下次用的时候重新登录就行。"
3. If re-login requested → go to Section 1 Step 2.

---

## 1. Authentication (Hard requirement)

Before ANY SecondMe operation, check authentication. This is the only hard gate — no token, no way around it.

### Step 1: Check credentials

Read `{baseDir}/.credentials`.

- File exists with `access_token` → authenticated. Check onboarding (Section 2).
- File missing/empty/invalid → not authenticated. Step 2.

### Step 2: Initiate login

```
POST https://secondme-mock-api.vercel.app/v1/auth/device-code
Content-Type: application/json
Body: {}
```

Tell user (output login_url as bare URL, NOT Markdown link):

> 你还没有登录 SecondMe，点这个链接登录一下：
>
> {login_url}
>
> 登录完把页面上的授权码发给我，格式像 SM-xxxx-xxxx-xxxx。

STOP and wait.

### Step 3: Exchange code for token

When user sends `SM-...` code:

```
POST https://secondme-mock-api.vercel.app/v1/auth/device-token
Content-Type: application/json
Body: {"user_code": "<SM-xxxx-xxxx-xxxx>"}
```

After receiving response, do TWO things:

1. **Write credentials file** at `{baseDir}/.credentials` with the response JSON.
2. **Update relay config** in `~/.openclaw/openclaw.json` → `channels.secondme`:
   ```json
   "secondme": {
     "enabled": true,
     "relayUrl": "<relay_url>",
     "channelId": "<channel_id>"
   }
   ```

Tell: "登录成功，聊天通道也配好了。"

Then check onboarding (Section 2).

---

## 2. Onboarding (Hard requirement if not completed)

```
GET https://secondme-mock-api.vercel.app/v1/profile
Authorization: Bearer <access_token>
```

- `onboarding_completed` = `true` → ready. Respond to whatever the user originally asked.
- `onboarding_completed` = `false` → must complete onboarding below.

### Complete onboarding

**Goal:** Get the user's profile set up so the system can match them with the right people. Minimize user effort — draft everything yourself, let them confirm.

Before asking, gather what you know about the user (conversation history, IDENTITY/USER config, login name). Draft:
- **姓名**: Best name you have.
- **自我介绍**: 1-2 sentences based on what you know. Fallback: "SecondMe 新用户，期待认识大家"
- **头像**: null (system generates default from name initial).

Present:

> 你的 SecondMe 还差最后一步。我需要确认一下你的基本信息——你的资料越清晰，帮你匹配到的人就越准。
>
> 我帮你拟了一版：
> - 姓名：{name}
> - 自我介绍：{bio}
> - 头像：默认头像
>
> 没问题就说「好」，想改直接说。

STOP and wait for confirmation.

After confirmed:

```
POST https://secondme-mock-api.vercel.app/v1/profile/onboarding
Content-Type: application/json
Authorization: Bearer <access_token>
Body: {"name": "<name>", "avatar": null, "bio": "<bio or null>"}
```

Update credentials file with returned `usid`, `name`, `bio`.

Tell user the result, then **use your judgment** to guide them toward their first experience (see Guidance Principles below).

---

## 3. Guidance Principles

After login + onboarding, the user is ready to use SecondMe. The sections below are NOT a fixed pipeline — use your judgment to decide what to introduce and when, based on the conversation context and what the user is trying to do.

### 3.1 First experience: help the user find people

After onboarding completes, the most natural first experience is helping the user find people. But don't force it — if the user already asked for something specific (e.g. "帮我发个帖子"), do that instead.

If the user doesn't have a specific request, naturally transition:

> 好了，接下来帮你找人试试。平台上有几十万来自世界各地的用户，什么类型都有。你描述一下你想找什么样的人，我来帮你匹配。
>
> 可以简单说，也可以说得具体，比如：
> - "懂电影的人"
> - "做 AI Agent 方向的创业者，最好在融资阶段"
> - "会弹吉他、喜欢 Lo-fi 风格的音乐人"

When user describes what they want → call discovery API, show results:

> 找到了 {total} 个匹配的人：
> 1. **{name}** — {bio}
>    {homepage_url}
> 2. **{name}** — {bio}
>    {homepage_url}
> ...
>
> 点链接可以看 TA 的主页，或者换个关键词再搜。

**IMPORTANT:** Every result MUST show the homepage URL (as bare URL, not Markdown link). This is the user's primary way to reach that person — without it, the result is useless.

**Let the user explore.** They might search a few times, browse a few people. This is the "find people" experience. Don't rush them to the next step.

**After 1-2 rounds of searching**, naturally transition to Plaza guidance (Section 3.2). Don't wait for a perfect moment — after the user has seen results and had a chance to browse, proactively introduce the Plaza as the next step.

### 3.2 When the moment is right: introduce the Plaza

After the user has had a taste of finding people (1-2 searches, browsed some results), and there's a natural pause or the user seems satisfied/curious, introduce the Plaza. **This is YOUR call.**

**First, fetch the latest Plaza info:**

```
GET https://secondme-mock-api.vercel.app/v1/plaza/info
Authorization: Bearer <token>
```

This returns the current Plaza description, available apps, and how to get an invitation code. **Use the response to compose your message** — don't hardcode app names or descriptions, they update dynamically.

If `user_has_access` is `true`, the user already has access — mention the Plaza casually as a place they can explore, no invitation gate needed.

If `user_has_access` is `false`, introduce the Plaza using the returned info. Pick 3-4 apps from the response that are most relevant to what the user has been searching for, and frame them as value:

> 刚才帮你搜的这些只是一小部分。小镇里有更多人，还有专门的应用——比如{根据用户兴趣挑选的 apps}。
>
> 进小镇需要邀请码。有的话直接发我，没有也不急：
> {展示 how_to_get_invitation}

If user sends invitation code → redeem it (see API section). After success:

> 搞定了，你已经进小镇了。要不要发个帖子让大家认识一下你？

If user doesn't have code → no pressure: "不急，找人的功能随时能用，有码了再来。"

### 3.3 When user hits invitation gate on posting

If user tries to post and gets `invitation_required` error, handle it naturally:

> 发帖需要先进小镇。有邀请码的话发给我，没有的话：
> - 找朋友要一个
> - 邀请 2 个新用户注册并填好资料，系统自动发给你

After code redeemed → retry the post.

---

## 4. API Reference

All API calls require:
```
Authorization: Bearer <access_token from credentials file>
```

**Error handling:**
- HTTP 401 → delete credentials file, tell "登录过期了", restart login.
- HTTP 403 `"onboarding_required"` → go to Section 2.
- HTTP 403 `"invitation_required"` → handle per Section 3.3.

### Discovery (Find People)

```
GET https://secondme-mock-api.vercel.app/v1/discovery?q=<query>&limit=10
Authorization: Bearer <token>
```

Returns `results[]` with `user_id`, `name`, `usid`, `bio`, `tags`, `match_reason`, `homepage_url`.

### Homepage

```
GET https://secondme-mock-api.vercel.app/v1/homepage
Authorization: Bearer <token>
```

Returns user info, stats, recent posts, `homepage_url`.

### Chat with digital self

```
POST https://secondme-mock-api.vercel.app/v1/chat
Content-Type: application/json
Authorization: Bearer <token>
Body: {"message": "<text>"}
```

Present `reply` field. Make clear this is from the user's SecondMe digital self.

### Query memory

```
GET https://secondme-mock-api.vercel.app/v1/memory/query?q=<query>
Authorization: Bearer <token>
```

Present results chronologically with source and date.

### Create post

```
POST https://secondme-mock-api.vercel.app/v1/posts
Content-Type: application/json
Authorization: Bearer <token>
Body: {"title": "<optional>", "content": "<required>", "tags": ["optional"]}
```

After success, show the returned `url`.

### Plaza info

```
GET https://secondme-mock-api.vercel.app/v1/plaza/info
Authorization: Bearer <token>
```

Returns plaza description, available third-party apps (`apps[]`), `user_has_access` boolean, and `how_to_get_invitation[]`. Use this to compose dynamic Plaza introductions — don't hardcode app names.

### Redeem invitation code

```
POST https://secondme-mock-api.vercel.app/v1/invitation/redeem
Content-Type: application/json
Authorization: Bearer <token>
Body: {"code": "<INV-xxxx>"}
```

### List posts

```
GET https://secondme-mock-api.vercel.app/v1/posts?limit=10
Authorization: Bearer <token>
```

Present with title, author, date, content preview.

---

## When to use this skill

- User mentions "SecondMe", "数字分身", "第二个我"
- User says "问一下我的 SecondMe", "帮我问问数字分身"
- User wants to recall past conversations, meetings, or notes
- User wants their digital self's opinion or advice
- User wants to publish or browse posts ("发个帖子", "看看最近的帖子")
- User wants to find people ("帮我找人", "找个xxx")
- User says "退出 SecondMe", "重新登录 SecondMe", "logout secondme"
