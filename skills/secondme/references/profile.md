# Profile

## Contents

- [Read Profile](#read-profile)
- [Guided Profile Review](#guided-profile-review)
- [Update Profile](#update-profile)
- [Optional First-Run Handoff](#optional-first-run-handoff)
- [Interest Tags (Shades)](#interest-tags-shades)
- [Soft Memory](#soft-memory)

## Read Profile

```
GET {BASE}/api/secondme/user/info
Authorization: Bearer <accessToken>
```

Useful fields:
- `name`
- `avatar`
- `aboutMe`
- `originRoute`
- `homepage`

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

Update only the fields the user wants changed:

```
POST {BASE}/api/secondme/user/profile
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

```
GET {BASE}/api/secondme/user/shades
Authorization: Bearer <accessToken>
```

Returns the user's public interest tags. Only tags with `hasPublicContent=true` are included.

Useful fields:

- `shades[]`
  - `id`
  - `shadeName` — tag name
  - `shadeIcon` — tag icon
  - `confidenceLevel` — `VERY_HIGH`, `HIGH`, `MEDIUM`, `LOW`, or `VERY_LOW`
  - `shadeDescription` — tag description
  - `shadeContent` — tag content
  - `sourceTopics` — source topic list
  - `shadeNamePublic` — public-facing tag name
  - `shadeDescriptionPublic` — public-facing description
  - `shadeContentPublic` — public-facing content
  - `hasPublicContent`

When presenting shades to the user, prefer the public-facing fields (`shadeNamePublic`, `shadeDescriptionPublic`, `shadeContentPublic`) when they are non-null.

## Soft Memory

```
GET {BASE}/api/secondme/memory/key/search?keyword=<optional>&pageNo=1&pageSize=20
Authorization: Bearer <accessToken>
```

Retrieves the user's soft memory entries (personal knowledge base).

Query params:

- `keyword` (optional): search keyword; returns all entries if empty
- `pageNo` (optional, default 1): page number, must be >= 1
- `pageSize` (optional, default 20): items per page, range 1-100

Response fields:

- `list[]`
  - `id`
  - `factObject` — what the fact is about
  - `factContent` — fact content
  - `createTime` — creation timestamp in milliseconds
  - `updateTime` — last update timestamp in milliseconds
- `total` — total count

Rules:

- Do not merge soft memory results with local memory or Key Memory results unless the user explicitly asks for combined output
- When the user asks about what SecondMe knows about them, soft memory is a good source to check alongside the profile
