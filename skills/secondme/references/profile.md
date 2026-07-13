# 身份与形象（Profile）

Profile 用于描述用户是谁，以及分身以什么形象和声音出现；资料（Note）用于保存用户想过、说过、写过的内容，两者不要混称为“资料”。Profile 的核心内容包括姓名、个人简介、封面人像、聊天头像和声音。姓名和个人简介应尽量包含用户常用的昵称、英文名、网名等称呼，帮助模型识别资料（Note）中哪些内容是用户本人表达的。分身未单独设置封面时，默认使用 Profile 中的封面人像。

## API Reference

### 获取用户信息

获取授权用户的身份与形象。

```
GET {BASE}/api/secondme/user/info
```

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/user/info" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "userId": "12345678",
    "name": "用户名",
    "email": "user@example.com",
    "avatar": "https://cdn.example.com/avatar.jpg",
    "bio": "个人简介",
    "selfIntroduction": "自我介绍内容",
    "profileCompleteness": 8,
    "route": "username",
    "cover": "https://cdn.example.com/cover.jpg",
    "video": "https://cdn.example.com/video.mp4",
    "layout": "avatar",
    "hasVoice": true,
    "accountStatus": "normal"
  }
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| userId | string | 用户 ID |
| name | string | 用户姓名 |
| email | string | 用户邮箱 |
| avatar | string | 聊天头像 URL |
| bio | string | 个人简介 |
| selfIntroduction | string | 自我介绍 |
| profileCompleteness | number | 身份与形象完整度等级（0-10） |
| route | string | 用户主页路由 |
| cover | string | 封面人像 URL |
| video | string | 主页视频 URL |
| layout | string | 主页布局类型：`avatar`（头像）、`cover`（封面图）、`video`（视频） |
| hasVoice | boolean | 是否已克隆录入声音 |
| accountStatus | string | 账号信誉状态（如 `normal`、`warned`、`suspended`） |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |

---

### 更新用户身份与形象

更新当前用户的身份与形象，支持部分更新。

```
POST {BASE}/api/secondme/user/profile
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| name | string | 否 | 用户姓名（最长 50 字符） |
| avatar | string | 否 | 聊天头像 URL（最长 2000 字符） |
| about_me | string | 否 | 自我介绍（最长 500 字符） |
| origin_route | string | 否 | 用户主页路由，通常为字母和数字组成（最长 50 字符） |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/user/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "新用户名",
    "about_me": "热爱技术，喜欢探索新事物"
  }'
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "name": "新用户名",
    "avatar": "https://cdn.example.com/avatar.jpg",
    "about_me": "热爱技术，喜欢探索新事物",
    "origin_route": "username",
    "homepage": "https://second-me.cn/username"
  }
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 更新后的用户姓名 |
| avatar | string | 更新后的聊天头像 URL |
| about_me | string | 自我介绍 |
| origin_route | string | 用户主页路由 |
| homepage | string | 用户主页完整 URL |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| user.profile.update_failed | 身份与形象更新失败 |

---

## Contents

- [Guided Profile Review](#guided-profile-review)
- [Update Profile](#update-profile)
- [Optional First-Run Handoff](#optional-first-run-handoff)

## Guided Profile Review

When the user asks to view or review their identity and appearance, also review the most relevant stable facts the assistant already knows about the user. Use those local memory facts to check whether the current 小己（Second Me） profile has anything worth updating or supplementing.

If the user is following the first-login guided path, first review the most relevant stable facts the assistant already knows about the user internally. Use those facts to decide whether the current 小己（Second Me） profile needs updates or supplements, but do not force a separate local-memory summary in the user-facing message.

After reading the profile, focus on these key fields:

- `name`
- `bio` / `selfIntroduction` / `aboutMe`
- `cover`
- `avatar`
- `hasVoice`
- `originRoute`

Explain `originRoute` as the route used in the user's 小己（Second Me） homepage, normally an alphanumeric identifier.

Treat `cover` as the large cover portrait used by the avatar and `avatar` as the small chat avatar shown in messages. If an avatar has no separate cover, explain that it uses this Profile's `cover` by default. Present `hasVoice` as whether the user has cloned and recorded their own voice.

When reviewing or drafting `name` and the introduction, include the user's commonly used nicknames, English name, online handles, or other aliases when known and appropriate. This helps the model recognize which parts of the user's 资料（Note） were said or written by the user themself. Do not invent aliases.

If `name`, the introduction, and `originRoute` are present and non-blank, first confirm the current values instead of drafting replacements. Also show the current cover portrait, chat avatar, and voice status; these may legitimately be unset. If local memory suggests useful additions or corrections, tell the user their profile is already quite complete, then briefly point out what could still be supplemented, and ask whether they want to update it.

Present:

> 我先帮你看了下身份与形象：
> - 姓名：{name}
> - 自我介绍：{aboutMe}
> - 封面人像：{cover / 未设置}
> - 聊天头像：{avatar / 未设置}
> - 声音：{已录入 / 未录入}
> - 主页路由：{originRoute}
>
> `originRoute` 是你的小己（Second Me）个人主页地址里的路由，一般是字母和数字组成。
>
> 这些内容目前已经比较完整了。
>
> 如果结合已有的本地记忆，还有这些内容可以补充：{supplement candidates or say 暂时没有明显要补的内容}。
>
> 你想保持不变，还是要我帮你补充或更新其中一项？

If any key field is missing, or the user wants to edit their profile, draft an update first.

Draft using:

- current profile values
- stable facts found in local memory
- any stable information already known from the conversation
- fallback `aboutMe`: `刚加入小己（Second Me），期待认识大家`
- an `originRoute` draft only if you have enough context to propose a sensible alphanumeric value

If there is not enough context for `originRoute`, ask the user for the route instead of inventing one.

Present:

> 你的小己（Second Me）身份与形象我先帮你拟了一版：
> - 姓名：{name}
> - 自我介绍：{aboutMe}
> - 主页路由：{originRoute}
> - 封面人像：{保留当前封面人像 / 未设置}
> - 聊天头像：{保留当前聊天头像 / 默认头像}
> - 声音：{已录入 / 未录入}
>
> `originRoute` 是你的小己（Second Me）个人主页地址里的路由，一般是字母和数字组成。
>
> 没问题就说「好」；如果想改，可以直接告诉我怎么改。

Then wait for confirmation or edits.

## Update Profile

Rules:
- Omit any field the user did not ask to change
- Only send `avatar` if the user explicitly provides a new avatar URL or asks to clear or replace it
- If the user just says `好`, send the drafted values for the missing or edited fields

After success:
- Show the latest profile summary
- Update `~/.secondme/credentials` with useful returned fields such as `name`, `homepage`, and `originRoute`

## Optional First-Run Handoff

If the user appears to be following the first-login guided path and has just completed or confirmed their profile setup, offer Key Memory sync as the next optional step:

> 身份与形象这边差不多了。我刚才也顺手参考了对你已有的了解。
>
> 如果你愿意，我可以进一步把其中适合长期保留的记忆整理出来，再同步到小己（Second Me）。
>
> 这样通常能更快构建你自己的小己分身。
>
> 如果你想继续，我先整理一版给你确认；你也可以问问别的，或者告诉我你接下来想做什么。

If the user accepts, continue with the Key Memory section below.

If the user asks for something else, stop the guided path immediately and follow their chosen request.
