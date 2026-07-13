# Profile

## API Reference

### 获取用户信息

获取授权用户的基本信息。

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
| avatar | string | 头像 URL |
| bio | string | 个人简介 |
| selfIntroduction | string | 自我介绍 |
| profileCompleteness | number | 资料完整度等级（0-10） |
| route | string | 用户主页路由 |
| cover | string | 主页封面图 URL |
| video | string | 主页视频 URL |
| layout | string | 主页布局类型：`avatar`（头像）、`cover`（封面图）、`video`（视频） |
| hasVoice | boolean | 是否配置了自定义语音 |
| accountStatus | string | 账号信誉状态（如 `normal`、`warned`、`suspended`） |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |

---

### 获取用户兴趣标签

获取用户的兴趣标签（仅返回有公开内容的标签）。

```
GET {BASE}/api/secondme/user/shades
```

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/user/shades" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "shades": [
      {
        "id": 123,
        "shadeName": "科技爱好者",
        "shadeIcon": "https://cdn.example.com/icon.png",
        "confidenceLevel": "HIGH",
        "shadeDescription": "热爱科技",
        "shadeDescriptionThirdView": "他/她热爱科技",
        "shadeContent": "喜欢编程和数码产品",
        "shadeContentThirdView": "他/她喜欢编程和数码产品",
        "sourceTopics": ["编程", "AI"],
        "shadeNamePublic": "科技达人",
        "shadeIconPublic": "https://cdn.example.com/public-icon.png",
        "confidenceLevelPublic": "HIGH",
        "shadeDescriptionPublic": "科技爱好者",
        "shadeDescriptionThirdViewPublic": "一位科技爱好者",
        "shadeContentPublic": "热爱科技",
        "shadeContentThirdViewPublic": "他/她热爱科技",
        "sourceTopicsPublic": ["科技"],
        "hasPublicContent": true
      }
    ]
  }
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| shades | array | 兴趣标签列表 |
| shades[].id | number | 标签 ID |
| shades[].shadeName | string | 标签名称 |
| shades[].shadeIcon | string | 标签图标 URL |
| shades[].confidenceLevel | string | 置信度：`VERY_HIGH`、`HIGH`、`MEDIUM`、`LOW`、`VERY_LOW` |
| shades[].shadeDescription | string | 标签描述 |
| shades[].shadeDescriptionThirdView | string | 第三人称描述 |
| shades[].shadeContent | string | 标签内容 |
| shades[].shadeContentThirdView | string | 第三人称内容 |
| shades[].sourceTopics | array | 来源主题 |
| shades[].shadeNamePublic | string | 公开标签名称 |
| shades[].shadeIconPublic | string | 公开图标 URL |
| shades[].confidenceLevelPublic | string | 公开置信度 |
| shades[].shadeDescriptionPublic | string | 公开描述 |
| shades[].shadeDescriptionThirdViewPublic | string | 公开第三人称描述 |
| shades[].shadeContentPublic | string | 公开内容 |
| shades[].shadeContentThirdViewPublic | string | 公开第三人称内容 |
| shades[].sourceTopicsPublic | array | 公开来源主题 |
| shades[].hasPublicContent | boolean | 是否有公开内容 |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |

---

### 获取用户软记忆

> **已弃用**: 此接口已被 `/api/secondme/memory/key/search` 替代，建议使用 Key Memory 搜索接口。本接口保留用于向后兼容。

获取用户的软记忆数据（个人知识库），支持分页和搜索。

```
GET {BASE}/api/secondme/user/softmemory
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词 |
| pageNo | integer | 否 | 页码（默认: 1，最小: 1） |
| pageSize | integer | 否 | 每页大小（默认: 20，最大: 100） |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/user/softmemory?keyword=爱好&pageNo=1&pageSize=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": 456,
        "factObject": "兴趣爱好",
        "factContent": "喜欢阅读科幻小说",
        "createTime": 1705315800000,
        "updateTime": 1705315800000
      }
    ],
    "total": 100
  }
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| list | array | 软记忆列表 |
| list[].id | number | 软记忆 ID |
| list[].factObject | string | 事实对象/分类 |
| list[].factContent | string | 事实内容 |
| list[].createTime | number | 创建时间（毫秒时间戳） |
| list[].updateTime | number | 更新时间（毫秒时间戳） |
| total | number | 总数 |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |

---

### 更新用户资料

更新当前用户的个人资料信息，支持部分更新。

```
POST {BASE}/api/secondme/user/profile
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| name | string | 否 | 用户姓名（最长 50 字符） |
| avatar | string | 否 | 头像 URL（最长 2000 字符） |
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
| avatar | string | 头像 URL |
| about_me | string | 自我介绍 |
| origin_route | string | 用户主页路由 |
| homepage | string | 用户主页完整 URL |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| user.profile.update_failed | 资料更新失败 |

---

## Contents

- [Guided Profile Review](#guided-profile-review)
- [Update Profile](#update-profile)
- [Optional First-Run Handoff](#optional-first-run-handoff)
- [Interest Tags (Shades)](#interest-tags-shades)
- [Soft Memory](#soft-memory)

## Guided Profile Review

When the user asks to view or review their personal information, also review the most relevant stable facts the assistant already knows about the user. Use those local memory facts to check whether the current SecondMe profile has anything worth updating or supplementing.

If the user is following the first-login guided path, first review the most relevant stable facts the assistant already knows about the user internally. Use those facts to decide whether the current SecondMe profile needs updates or supplements, but do not force a separate local-memory summary in the user-facing message.

After reading the profile, focus on these key fields:

- `name`
- `aboutMe`
- `originRoute`

Explain `originRoute` as the route used in the user's SecondMe homepage, normally an alphanumeric identifier.

If all three fields are present and non-blank, first confirm the current values instead of drafting replacements. If local memory suggests useful additions or corrections, tell the user their profile is already quite complete, then briefly point out what could still be supplemented, and ask whether they want to update it.

Present:

> 我先帮你看了下资料：
> - 姓名：{name}
> - 自我介绍：{aboutMe}
> - 主页路由：{originRoute}
>
> `originRoute` 是你 SecondMe 个人主页地址里的路由，一般是字母和数字组成。
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
- fallback `aboutMe`: `SecondMe 新用户，期待认识大家`
- an `originRoute` draft only if you have enough context to propose a sensible alphanumeric value

If there is not enough context for `originRoute`, ask the user for the route instead of inventing one.

Present:

> 你的 SecondMe 资料我先帮你拟了一版：
> - 姓名：{name}
> - 自我介绍：{aboutMe}
> - 主页路由：{originRoute}
> - 头像：{保留当前头像 / 默认头像}
>
> `originRoute` 是你 SecondMe 个人主页地址里的路由，一般是字母和数字组成。
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

> 资料这边差不多了。我刚才也顺手参考了对你已有的了解。
>
> 如果你愿意，我可以进一步把其中适合长期保留的记忆整理出来，再同步到 SecondMe。
>
> 这样通常能更快构建你自己的 SecondMe。
>
> 如果你想继续，我先整理一版给你确认；你也可以问问别的，或者告诉我你接下来想做什么。

If the user accepts, continue with the Key Memory section below.

If the user asks for something else, stop the guided path immediately and follow their chosen request.

## Interest Tags (Shades)

When presenting shades to the user, prefer the public-facing fields (`shadeNamePublic`, `shadeDescriptionPublic`, `shadeContentPublic`) when they are non-null.

## Soft Memory

Rules:

- Do not merge soft memory results with local memory or Key Memory results unless the user explicitly asks for combined output
- When the user asks about what SecondMe knows about them, soft memory is a good source to check alongside the profile
