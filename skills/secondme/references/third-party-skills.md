# Third-Party Skills

## API Reference

> **Doc source:** https://develop-docs.second.me/zh/docs/secondme/skills
>
> Fetch the doc page above for all endpoint definitions (app catalog, skill detail,
> execution RPC), request parameters, response fields, and error codes.

## Contents

- [Overview](#overview)
- [Discover Available Apps](#discover-available-apps)
- [Fetch Skill Detail And Bundle](#fetch-skill-detail-and-bundle)
- [Install Or Sync The Bundle Locally](#install-or-sync-the-bundle-locally)
- [Execution Boundary](#execution-boundary)
- [OAuth Authorization Error Handling](#oauth-authorization-error-handling)
- [Output Summary](#output-summary)

## Overview

Use this section when the user wants things like:

- `看看有什么第三方技能`
- `可安装技能有哪些`
- `浏览技能目录`
- `查看 skill catalog`
- `安装外部技能`
- `安装第三方 skill`
- `刷新技能目录`
- `同步某个技能`
- `重装某个外部 skill`

This section is responsible for:

- listing installable third-party apps that provide external skills
- showing a selected skill's install metadata
- fetching a skill bundle by `skillKey`
- installing the returned bundle into the local skill root
- refreshing or re-installing an already installed bundle from the latest server payload

This section is not responsible for:

- executing an installed skill
- calling `mcp/{integrationKey}/rpc` during installation
- treating `toolAllow` as an execution entrypoint

## Discover Available Apps

Rules:

- stop and report failure if the request does not succeed
- use the returned app list as the source of truth for what can be installed
- the server already sorts apps as: apps with skills first, featured apps second, other apps last
- only treat apps with non-empty `skills` as installable or usable
- the server only returns approved skill versions; do not surface unapproved versions
- when listing third-party apps, always show the app address together with the app name and description
- present useful app fields such as `appName`, `appDescription`, and `appStoreUrl`
- for each app, present the nested skill fields `integrationKey`, `skillKey`, `displayName`, `description`, and `version`
- if the user did not specify a `skillKey`, treat this as a catalog-browsing step and help them choose from the returned list
- when showing the app page, use the returned `appStoreUrl`; it should be in the form `https://appstore.second-me.cn/apps/{slug}`

## Fetch Skill Detail And Bundle

When the user chooses a `skillKey`, fetch the install payload.

Verify the response includes the install metadata and `generatedSkillFiles`.

Only fetch detail for a `skillKey` that came from the current approved app catalog response.

## Install Or Sync The Bundle Locally

Install using the server-provided bundle exactly as returned.

Rules:

- use `skillKey` as the local directory name
- create that directory under the current local skill root
- do not generate or rewrite `SKILL.md` yourself
- preserve server-provided file contents exactly
- write every file present in `generatedSkillFiles`, not only `SKILL.md`
- today the bundle is expected to include `SKILL.md`, `prompt.md`, and `prompt_short.md`
- if the server later adds more bundle files, write those too
- if the user asks to sync or re-install, fetch the latest bundle again and overwrite the local bundle with the server-returned files

Why this matters:

- `SKILL.md` is metadata and the entry declaration
- `prompt_short.md` is the short prompt injection
- `prompt.md` is the long prompt injection

If the current runtime exposes a higher-level local skill installation action, it may be used, but the final on-disk contents must still match `generatedSkillFiles` exactly.

## Execution Boundary

Rules:

- do not call the RPC endpoint during installation
- do not use `toolAllow` as a substitute for installation or execution
- only the installed runtime skill should decide when to call the RPC path later

## OAuth Authorization Error Handling

If a later skill use attempt fails because the user has not authorized the underlying app, the RPC response may include:

- `error.code = -32010`
- `error.data.businessCode = third_party_agent.oauth.authorization_required`
- `error.data.appStoreUrl = https://appstore.second-me.cn/apps/{slug}`

When this happens:

- tell the user this app has not been authorized yet
- show them the returned `appStoreUrl` as the place to authorize
- tell them to come back and retry after authorizing
- if `appStoreUrl` is present, output it exactly as returned

Suggested wording:

> 这个技能对应的三方应用你还没有授权。
>
> 先打开这个应用页完成授权：
>
> https://appstore.second-me.cn/apps/{slug}
>
> 授权完再回来重试就行。

## Output Summary

At the end, report:

- what was discovered
- which `skillKey` was selected
- whether detail fetch succeeded
- which files were installed locally
- whether installation or sync completed or failed

If installation cannot continue because the detail payload is missing `generatedSkillFiles`, stop and report that the server response is incomplete rather than fabricating local files.
