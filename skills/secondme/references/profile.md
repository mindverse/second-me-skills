# 身份与形象（Profile）

身份与形象（Profile）用于描述用户是谁，以及分身以什么形象和声音出现；资料（Note）用于保存用户想过、说过、写过的内容，两者不要混称为“资料”。身份与形象的核心内容包括姓名、自我介绍、封面人像、聊天头像和声音。`name` 只保存用户最常用的大名；昵称、英文名、网名等其他称呼写入 `about_me`，共同作为系统从资料中识别用户相关内容和本人发言的依据。分身未单独设置封面时，默认使用身份与形象中的封面人像。

字段语义映射：

- `bio` 表示内核（Core）。这是历史遗留字段名，不是自我介绍；当前技能只读不可写。
- `about_me` 表示用户的自我介绍。读取用户信息时，其值来自 GET 响应的 `selfIntroduction`；更新时写入 POST 请求的 `about_me`。
- `origin_route` 表示主页路由。读取用户信息时，其值来自 GET 响应的 `route`；更新时写入 POST 请求的 `origin_route`。
- `profileCompleteness` 是 API 字段名；面向用户一律称为**对齐度**，不得展示为“完整度”。分值直接使用接口返回的 0–10，不自行计算。

下文统一使用 `about_me` 和 `origin_route`，不得将 `bio` 当作自我介绍。

## API 参考

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
    "bio": "系统根据记忆归纳形成的内核内容",
    "selfIntroduction": "用户填写的自我介绍",
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
| bio | string | 内核内容（历史遗留字段名，当前技能只读） |
| selfIntroduction | string | 用户填写的自我介绍，读取后作为 `about_me` 使用 |
| profileCompleteness | number | 身份与形象对齐度（0–10；对外使用该名称） |
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
| cover | string | 否 | 封面人像 URL（最长 2000 字符）；`""` 表示清空 |
| about_me | string | 否 | 自我介绍（最长 500 字符） |
| origin_route | string | 否 | 用户主页路由，通常为字母和数字组成（最长 50 字符） |

所有字段均可选，未传字段保持原值。多字段更新不是原子操作；失败时先重新获取用户信息，确认哪些字段已更新，再决定是否重试。

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
    "cover": "https://cdn.example.com/cover.jpg",
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
| cover | string | 更新后的封面人像 URL（清空时为空字符串） |
| about_me | string | 自我介绍 |
| origin_route | string | 用户主页路由 |
| homepage | string | 用户主页完整 URL |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| user.profile.update_failed | 身份与形象更新失败 |

---

### 上传图片到 CDN

用户为 `avatar` 或 `cover` 提供本地图片时，先上传并把返回的 `data.url` 写入 Profile；不得把本地路径直接写入字段。

```text
POST {BASE}/api/cdn/upload
```

请求体使用 `multipart/form-data`，字段名为 `file`，鉴权仍放在 `Authorization: Bearer`：

```bash
curl -X POST "{BASE}/api/cdn/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/image.png"
```

成功响应的 `data.url` 是公开 URL，`data.key` 是 CDN 路径。HTTP 状态可能仍为 200，需同时检查响应体 `code`；上传失败时不得继续更新对应图片字段。

---

## 目录

- [身份与形象检查和首次引导](#guided-profile-review)
- [更新身份与形象](#update-profile)
- [首次运行的可选衔接流程](#optional-first-run-handoff)

<a id="guided-profile-review"></a>

## 身份与形象检查和首次引导

本节负责两类入口：用户主动查看或编辑身份与形象；以及 `connect.md` 完成登录后，在没有其他明确待办时交接过来的首次使用引导。

进入本节前应已按主 `SKILL.md` 的统一规则读取用户信息。`firstTimeLocalConnect = true` 且用户是从安装引导进入登录，或登录前没有其他明确任务时，不要重复安装路线图，也不要先询问用户是否需要引导。第一条身份检查消息以「登录成功！」开头，把登录确认和第一个可填写项放在同一条消息中。如果登录只是其他明确任务的前置条件，不运行首次引导，直接回到原任务。

当用户要求查看或检查自己的身份与形象时，同时检查智能体已经了解的、与用户最相关的稳定事实。使用这些本地记忆事实判断用户当前的小己（Second Me）身份与形象是否有值得更新或补充的内容。

如果用户正在进行首次本地连接的引导流程，先在内部检查智能体已经了解的、与用户最相关的稳定事实。用这些事实判断用户当前的小己（Second Me）身份与形象是否需要更新或补充，但不要在面向用户的消息中强行加入一份单独的本地记忆摘要。

读取身份与形象后，重点检查以下字段：

- `name`
- `about_me`（取自 GET 响应的 `selfIntroduction`）
- `bio`（内核，只读且不参与身份信息补全）
- `cover`
- `avatar`
- `hasVoice`
- `origin_route`（取自 GET 响应的 `route`）

`profileCompleteness` 仅用于展示接口给出的对齐度，不作为待填写字段。接口返回该值时，统一展示为「对齐度：{profileCompleteness}/10」；未返回时省略，不根据已填写字段数量自行推算。任何面向用户的身份与形象摘要、登录后提示和更新结果都不得使用“完整度”称呼这项分数。

向用户展示时，将这些字段分为：

- **身份**：最常用的大名 `name`，以及包含其他常见称呼的自我介绍 `about_me`
- **内核**：`bio`，只读且不作为待补全的身份字段
- **形象**：`cover` 和 `avatar`
- **声音**：`hasVoice`

说明 `origin_route` 是用户小己（Second Me）个人主页所使用的路由，通常由字母和数字组成。

将 `cover` 解释为分身使用的大幅封面人像，将 `avatar` 解释为消息中显示的小幅聊天头像。如果分身没有单独设置封面，说明它默认使用此身份与形象中的 `cover`。将 `hasVoice` 展示为用户是否已克隆录入自己的声音。

将 `name` 视为用户的主姓名字段，只填写一个最常用的大名，不得把真实姓名、昵称、英文名和网名全部拼接进去。其他可靠称呼应以自然语言写入 `about_me`，例如「大家也常叫我小林、Alex」。`name` 与 `about_me` 中的其他称呼共同帮助系统关联用户上传的资料（Note），并识别访谈等内容中哪些发言来自用户本人。不得编造称呼，也不得覆盖 `about_me` 中已有的有效介绍。仅有称呼列表不等于完整的自我介绍；如果 `about_me` 只有称呼信息，仍继续引导用户补充个人介绍，并把两部分合并保存。

在首次本地连接引导中，即使 `name` 已有内容，也要确认一次它是否为别人最常用的大名，并询问是否还有其他常见称呼。如果用户提供了多个名字但没有说明主次，追问哪一个是最常用的大名；确认后只将该名字写入 `name`，其他称呼合并进 `about_me`。

如果 `name` 为空，首次引导使用：

> 登录成功！我先检查了你的身份、形象和声音。我们先从身份开始。
>
> 大名和其他常见称呼会帮助小己从你后续上传的资料中，识别哪些内容与你有关、哪些话是你本人说的，例如访谈中属于你的发言。
>
> 别人一般怎么称呼你？可以把最常用的大名、昵称、英文名或网名一起告诉我。我会只把最常用的大名填入姓名，其他称呼整理进自我介绍。

如果 `name` 已有内容，首次引导使用：

> 登录成功！我先检查了你的身份、形象和声音。
>
> 当前记录的姓名是「{name}」。除此之外，别人还会用哪些昵称、英文名或网名称呼你？我会把这些称呼补充进自我介绍；如果没有，直接回复「没有」。

用户完成、拒绝或转向其他任务后，本次对话中不得再次重复首次引导。

如果 `name`、自我介绍 `about_me` 和 `origin_route` 都存在且非空，先让用户确认当前值，不要直接起草替代内容。同时展示当前的封面人像、聊天头像、声音状态和接口返回的对齐度；这些字段未设置也可能是正常情况。如果本地记忆中有值得补充或更正的内容，先告诉用户当前身份与形象已经与本人比较对齐，再简要指出仍可补充的内容，并询问用户是否要更新。

按以下格式展示：

> 我先帮你看了下身份与形象：
> - 姓名：{name}
> - 自我介绍：{about_me}
> - 封面人像：{cover / 未设置}
> - 聊天头像：{avatar / 未设置}
> - 声音：{已录入 / 未录入}
> - 主页路由：{origin_route}
> - 对齐度：{profileCompleteness}/10（接口未返回时省略）
>
> `origin_route` 是你的小己（Second Me）个人主页地址里的路由，一般是字母和数字组成。
>
> 这些身份与形象信息目前已经与本人比较对齐。
>
> 如果结合已有的本地记忆，还有这些内容可以补充：{补充候选内容；如果没有，则写“暂时没有明显要补的内容”}。
>
> 你想保持不变，还是要我帮你补充或更新其中一项？

如果有关键字段缺失，不要先展示一份带空项的清单，再提出含糊的问题。简要展示当前状态后，只询问一个明确的缺失字段。按照以下顺序逐项处理：

1. **姓名和其他称呼**：如果已知可靠称呼，先判断哪个是别人最常用的大名；无法判断时必须追问。`name` 草案只放一个最常用的大名，其他称呼写入 `about_me` 草案。信息不足时说明用途，并询问别人实际如何称呼用户，不要问用户偏好什么称呼：

   > 我们先补身份。大名和其他常见称呼会帮助小己从你后续上传的资料中，识别哪些内容与你有关、哪些话是你本人说的，例如访谈中属于你的发言。
   >
   > 别人一般怎么称呼你？可以把最常用的大名、昵称、英文名或网名一起告诉我。我会只把最常用的大名填入姓名，其他称呼整理进自我介绍。

2. **自我介绍**：保留刚刚整理出的其他称呼，再尽可能根据本地记忆中的稳定事实起草其余介绍。仅有称呼信息时仍视为需要补充。否则提供一个可直接填写的结构：

   > 接下来补一段自我介绍。请用 1–3 句话填写：「我是___，主要在做___，擅长或长期关注___。」不想填的部分可以删掉。

3. **主页路由**：仅在上下文足够充分时起草由字母和数字组成的路由。否则询问：

   > 你希望个人主页地址用什么英文或数字标识？例如 `linzhou` 或 `alex2026`。

4. **聊天头像**：请用户提供公开图片 URL 或本地图片；本地图片先上传到 CDN。
5. **封面人像**：处理方式同聊天头像；清空时发送 `"cover": ""`，并先取得用户确认。
6. **声音**：当前技能 API 只能检查 `hasVoice`。明确告诉用户前往小己应用录入或克隆声音，然后请用户回复 `录好了`，以便重新获取状态。

每轮只问一个问题，允许用户回复 `跳过`。如果用户一次提供多个名字，这仍视为同一个身份问题；主姓名不明确时只追问主姓名。收集完成后，仅展示将发生变化的字段并等待确认，其中 `name` 只含一个大名，其他称呼位于 `about_me`。

<a id="update-profile"></a>

## 更新身份与形象

规则：

- 省略用户未要求更改的所有字段
- 只有用户明确提供公开 URL、本地图片，或要求清空、替换时，才发送 `avatar` / `cover`
- 如果用户只回复 `好`，则发送为缺失字段或已编辑字段起草的值

图片字段处理：

- 公开 URL 直接使用；本地图片先通过[上传图片到 CDN](#上传图片到-cdn)，再写入 `data.url`
- 上传失败时报告错误，不更新该字段；不得写入本地文件路径
- 清空 `cover` 前确认，再发送 `"cover": ""`
- 多字段更新失败后，重新读取 Profile 确认最终状态

更新成功后：

- 重新调用 `GET {BASE}/api/secondme/user/info`，获取最新用户信息
- 使用刷新后的 Profile 展示最新身份与形象摘要
- 不得把 `name`、`homepage`、`origin_route` 或其他 Profile 字段写入 `~/.secondme/credentials`

<a id="optional-first-run-handoff"></a>

## 首次运行的可选衔接流程

如果用户正在进行首次本地连接的引导流程，并且已经完成、确认或明确跳过身份与形象字段，则通过一项具体操作衔接到资料（Note）：

> 身份、形象和声音这一步完成了。下一步，我们给分身补充基础资料。
>
> 请直接发来第一批你想过、说过或写过的内容；可以一次贴多段文字或多个链接，我会逐条整理成资料，保存前先让你确认。

如果用户提供了内容，继续执行下方的资料（Note）部分。

如果用户提出其他请求，立即停止引导流程，转而处理用户选择的请求。
