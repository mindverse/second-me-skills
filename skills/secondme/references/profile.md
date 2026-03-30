# Profile

## API Reference

> **Doc sources:**
> - https://develop-docs.second.me/zh/docs/secondme/profile (profile update)
> - https://develop-docs.second.me/zh/docs/secondme/user (user info, shades, soft memory)
>
> Fetch the relevant doc page for endpoint definitions, request parameters, response fields, and error codes.

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
