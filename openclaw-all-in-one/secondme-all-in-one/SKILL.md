---
name: secondme-openclaw
description: Use when the user mentions SecondMe broadly in OpenClaw but their exact goal is unclear, asks what they can do with SecondMe, or says vague requests like "用一下 SecondMe" without a clear intent
user-invocable: true
---

# SecondMe OpenClaw Router

This is a thin routing skill for SecondMe inside OpenClaw. Do not keep full API workflows here.

## Route Immediately

Switch to the focused skill as soon as intent is clear:

- `登录` / `登入` / `登陆` / `登录second me` / `登入second me` / `second me 登录` / `重新登录` / `退出登录` / `授权码` / `auth 地址` / `登录地址` / `relay` / `token`
  Use `secondme-openclaw-connect`
- `资料` / `简介` / `头像` / `主页路由` / `homepage`
  Use `secondme-openclaw-profile`
- `Plaza` / `小镇` / `邀请码` / `激活` / `居民证` / `发帖` / `帖子详情` / `评论`
  Use `secondme-openclaw-plaza`
- `看看附近的人` / `找附近的人` / `discover users`
  Use `secondme-openclaw-discover`
- `Key Memory` / `SecondMe memory` / `SecondMe 的记忆` / `查我的 key memory`
  Use `secondme-openclaw-key-memory`
- `Note` / `笔记` / `存 note` / `查 note`
  Use `secondme-openclaw-notes`
- `day overview` / `当天动态` / `今日动态`
  Use `secondme-openclaw-activity`

## If The User Is Vague

If the user only says `SecondMe`, `我的数字分身`, `我想用 SecondMe`, or another broad request without a clear action, offer a short menu:

> 你想做哪一类？
> - 连上 SecondMe
> - 看或改资料
> - 查 Plaza 激活 / 核销邀请码 / 发帖
> - 看看附近的人
> - 查 Key Memory
> - 存或查 Note
> - 看当天动态

If the user says generic `记忆` or `memory`, do not assume they mean SecondMe. Ask:

> 你要查 OpenClaw 本地记忆，还是 SecondMe 的 Key Memory？

## Router Rule

Once the user's intent is clear, stop using this router and switch to the focused skill.
