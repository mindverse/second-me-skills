---
name: secondme-external-skill-catalog
description: Use when the user wants to browse, discover, inspect, install, refresh, or re-install installable external SecondMe skills in OpenClaw, including skill catalogs, available skills, and local skill bundle installation
user-invocable: true
---

# SecondMe External Skill Catalog

This skill discovers and installs external SecondMe skill bundles for OpenClaw. It does not execute installed skills, does not call MCP business tools, and does not handle third-party business workflows after installation.

**Credentials file:** `{baseDir}/.credentials`

## Authentication Prerequisite

Before using this skill, read `{baseDir}/.credentials`.

- If it contains `accessToken`, continue
- If it only contains legacy `access_token`, continue but normalize later
- If the file is missing, empty, or invalid, switch to `secondme`

## Scope

Use this skill when the user says things like:

- `看看有什么第三方技能`
- `可安装技能有哪些`
- `浏览技能目录`
- `查看 skill catalog`
- `安装外部技能`
- `安装第三方 skill`
- `刷新技能目录`
- `重装某个外部 skill`

This skill is responsible for:

- listing installable external skills
- showing a selected skill's install metadata
- fetching a skill bundle by `skillKey`
- installing the returned bundle into the local OpenClaw skill root

This skill is not responsible for:

- executing an installed skill
- calling `mcp/{integrationKey}/rpc` during installation
- treating `toolAllow` as an execution entrypoint

## Discover Available Skills

Fetch the available skill catalog:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/skills/available
Authorization: Bearer <token>
```

Rules:

- Stop and report failure if this request does not succeed
- Use the returned list as the source of truth for what can be installed
- Present useful fields such as `skillKey`, `integrationKey`, `displayName`, `description`, `version`, `actions`, and `toolAllow`
- If the user did not specify a `skillKey`, treat this as a catalog-browsing step and help them choose from the returned list

## Fetch Skill Detail And Bundle

When the user chooses a `skillKey`, fetch the install payload:

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/skills/{skillKey}
Authorization: Bearer <token>
```

Verify the response includes the install metadata and `generatedSkillFiles`.

Expected detail fields include:

- `skillKey`
- `integrationKey`
- `displayName`
- `description`
- `version`
- `actions`
- `toolAllow`
- `generatedSkillFiles`

## Install The Bundle Locally

Install using the server-provided bundle exactly as returned.

Rules:

- Use `skillKey` as the local directory name
- Create that directory under the current OpenClaw local skill root
- Do not generate or rewrite `SKILL.md` yourself
- Preserve server-provided file contents exactly
- Write every file present in `generatedSkillFiles`, not only `SKILL.md`
- Today the bundle is expected to include `SKILL.md`, `prompt.md`, and `prompt_short.md`
- If the server later adds more bundle files, write those too

Why this matters:

- `SKILL.md` is metadata and the entry declaration
- `prompt_short.md` is the short prompt injection
- `prompt.md` is the long prompt injection

If the current runtime exposes a higher-level local skill installation action, it may be used, but the final on-disk contents must still match `generatedSkillFiles` exactly.

## Execution Boundary

Installed skills may later execute through:

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/mcp/{integrationKey}/rpc
```

Rules:

- Do not call this RPC endpoint during installation
- Do not use `toolAllow` as a substitute for installation or execution
- Only the installed runtime skill should decide when to call this RPC path later

## Output Summary

At the end, report:

- what was discovered
- which `skillKey` was selected
- whether detail fetch succeeded
- which files were installed locally
- whether installation completed or failed

If installation cannot continue because the detail payload is missing `generatedSkillFiles`, stop and report that the server response is incomplete rather than fabricating local files.
