# Third-Party Skills

## API Reference

### 发现可用应用

获取可安装的第三方应用列表，每个应用可包含一个或多个技能。

```
GET {BASE}/api/secondme/extensions/apps
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| pageNo | integer | 否 | 页码（默认: 1） |
| pageSize | integer | 否 | 每页大小（默认: 20） |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/extensions/apps?pageNo=1&pageSize=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "apps": [
      {
        "appName": "日程助手",
        "appDescription": "管理你的日程安排和待办事项",
        "appStoreUrl": "https://appstore.second-me.cn/apps/calendar-helper",
        "skills": [
          {
            "integrationKey": "calendar-helper",
            "skillKey": "calendar-manage",
            "displayName": "日程管理",
            "description": "创建、查看和管理日程安排",
            "version": "1.0.0"
          }
        ]
      }
    ],
    "total": 10
  }
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| apps | array | 应用列表 |
| apps[].appName | string | 应用名称 |
| apps[].appDescription | string | 应用描述 |
| apps[].appStoreUrl | string | 应用商店页面 URL |
| apps[].skills | array | 应用包含的技能列表 |
| apps[].skills[].integrationKey | string | 集成标识 |
| apps[].skills[].skillKey | string | 技能标识 |
| apps[].skills[].displayName | string | 技能显示名称 |
| apps[].skills[].description | string | 技能描述 |
| apps[].skills[].version | string | 技能版本 |
| total | number | 应用总数 |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |

---

### 获取技能详情

获取指定技能的详细信息，包括元数据和生成的技能文件。

```
GET {BASE}/api/secondme/extensions/detail/{skill_key}
```

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| skill_key | string | 是 | 技能标识 |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/extensions/detail/calendar-manage" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "skillKey": "calendar-manage",
    "integrationKey": "calendar-helper",
    "displayName": "日程管理",
    "description": "创建、查看和管理日程安排",
    "version": "1.0.0",
    "actions": [
      "create_event",
      "list_events",
      "delete_event"
    ],
    "toolAllow": ["calendar-helper/*"],
    "generatedSkillFiles": {
      "SKILL.md": "---\nname: calendar-manage\n...",
      "prompt.md": "# Calendar Management\n...",
      "prompt_short.md": "Manage calendar events..."
    }
  }
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| skillKey | string | 技能标识 |
| integrationKey | string | 集成标识 |
| displayName | string | 技能显示名称 |
| description | string | 技能描述 |
| version | string | 技能版本 |
| actions | array | 支持的操作列表 |
| toolAllow | array | 允许的工具调用范围 |
| generatedSkillFiles | object | 生成的技能文件，键为文件名，值为文件内容 |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| skill.not_found | 技能不存在 |

---

### 执行技能 RPC

通过 MCP 协议执行第三方技能的 RPC 调用。

```
POST {BASE}/api/secondme/extensions/mcp/{integration_key}/rpc
```

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| integration_key | string | 是 | 集成标识 |

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| method | string | 是 | RPC 方法名 |
| params | object | 否 | RPC 调用参数 |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/extensions/mcp/calendar-helper/rpc" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "list_events",
    "params": {
      "date": "2024-01-20"
    }
  }'
```

#### 响应

**成功 (200)**

```json
{
  "result": {
    "events": [
      {
        "title": "团队会议",
        "startTime": "2024-01-20T10:00:00Z",
        "endTime": "2024-01-20T11:00:00Z"
      }
    ]
  }
}
```

**OAuth 授权错误**

当用户尚未授权对应的第三方应用时，返回以下错误：

```json
{
  "error": {
    "code": -32010,
    "message": "OAuth authorization required",
    "data": {
      "businessCode": "third_party_agent.oauth.authorization_required",
      "appStoreUrl": "https://appstore.second-me.cn/apps/calendar-helper"
    }
  }
}
```

> **提示**: 收到此错误时，引导用户打开 `appStoreUrl` 完成应用授权，授权完成后重试。

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| result | object | RPC 调用结果，结构取决于具体技能 |
| error | object | 错误信息（仅在失败时返回） |
| error.code | number | 错误码 |
| error.message | string | 错误消息 |
| error.data.businessCode | string | 业务错误码 |
| error.data.appStoreUrl | string | 应用授权页面 URL |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| -32010 (third_party_agent.oauth.authorization_required) | 需要先在应用商店授权该第三方应用 |
| -32601 | 方法不存在 |
| -32602 | 参数无效 |

---

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
