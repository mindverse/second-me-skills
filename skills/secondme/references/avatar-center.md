# Avatar Center（分身中心）

管理分身（Avatar）、查看交互记录、配置 API Key 分发。

## Table of Contents

- [获取分身列表](#获取分身列表)
- [获取分身详情](#获取分身详情)
- [创建分身](#创建分身)
- [更新分身](#更新分身)
- [删除分身](#删除分身)
- [设置默认分身](#设置默认分身)
- [获取分身公开信息](#获取分身公开信息)
- [获取交互记录](#获取交互记录)
- [创建 API Key](#创建-api-key)
- [获取 API Key 列表](#获取-api-key-列表)
- [更新 API Key](#更新-api-key)
- [删除 API Key](#删除-api-key)
- [Workflow Guidelines](#workflow-guidelines)

---

## API Reference

### 获取分身列表

分页获取当前用户的所有分身。

```
GET {BASE}/api/secondme/avatar/list
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| pageNo | integer | 否 | 页码（默认: 1） |
| pageSize | integer | 否 | 每页大小（默认: 20，最大: 100） |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/avatar/list?pageNo=1&pageSize=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "total": 2,
    "list": [
      {
        "avatarId": 1,
        "type": "primary",
        "title": "My Avatar",
        "modes": { "textChat": true, "voiceCall": false },
        "distribution": { "apiEnabled": false, "wxappEnabled": false },
        "shareCode": "abc123",
        "usageCount": 10,
        "viewCount": 50,
        "createdAt": "2026-03-20 10:00:00"
      },
      {
        "avatarId": 2,
        "type": "custom",
        "title": "Sales Consultant",
        "scenarioPrompt": "你是一个专业的销售顾问...",
        "opening": "你好！有什么可以帮你的？",
        "modes": { "textChat": true, "voiceCall": true },
        "distribution": { "apiEnabled": true, "wxappEnabled": false },
        "shareCode": "def456",
        "usageCount": 5,
        "viewCount": 20,
        "createdAt": "2026-03-25 14:30:00"
      }
    ]
  }
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| total | number | 分身总数 |
| list[].avatarId | number | 分身 ID |
| list[].type | string | `primary`（默认分身，不可删除）或 `custom` |
| list[].title | string | 分身名称 |
| list[].scenarioPrompt | string | 场景提示词 |
| list[].opening | string | 开场白 |
| list[].modes | object | 交互模式配置 |
| list[].distribution | object | 分发渠道配置 |
| list[].shareCode | string | 分享码 |
| list[].usageCount | number | 已消耗配额 |
| list[].viewCount | number | 查看次数 |
| list[].createdAt | string | 创建时间 |

---

### 获取分身详情

获取指定分身的详细信息。

```
GET {BASE}/api/secondme/avatar/detail
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| avatarId | integer | 是 | 分身 ID |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/avatar/detail?avatarId=2" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "avatarId": 2,
    "type": "custom",
    "title": "Sales Consultant",
    "scenarioPrompt": "你是一个专业的销售顾问...",
    "opening": "你好！有什么可以帮你的？",
    "modes": { "textChat": true, "voiceCall": true },
    "distribution": { "apiEnabled": true, "wxappEnabled": false },
    "shareCode": "def456",
    "usageCount": 5,
    "viewCount": 20,
    "createdAt": "2026-03-25 14:30:00"
  }
}
```

---

### 创建分身

创建一个新的自定义分身。

```
POST {BASE}/api/secondme/avatar/create
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| title | string | 是 | 分身名称（最长 100 字符） |
| scenarioPrompt | string | 否 | 场景提示词（描述分身的任务和行为） |
| opening | string | 否 | 开场白（访客打开时的第一条消息） |
| modes | object | 否 | 交互模式：`{ "textChat": bool, "voiceCall": bool }` |
| distribution | object | 否 | 分发配置：`{ "apiEnabled": bool, "wxappEnabled": bool }` |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/avatar/create" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "产品咨询助手",
    "scenarioPrompt": "你是一个专业的产品咨询顾问，负责回答客户关于产品功能和价格的问题。",
    "opening": "你好！我是产品咨询助手，请问有什么可以帮您的？",
    "modes": { "textChat": true, "voiceCall": false },
    "distribution": { "apiEnabled": true, "wxappEnabled": false }
  }'
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "avatarId": 3,
    "type": "custom",
    "title": "产品咨询助手",
    "scenarioPrompt": "你是一个专业的产品咨询顾问...",
    "opening": "你好！我是产品咨询助手...",
    "modes": { "textChat": true, "voiceCall": false },
    "distribution": { "apiEnabled": true, "wxappEnabled": false },
    "shareCode": "ghi789",
    "usageCount": 0,
    "viewCount": 0
  }
}
```

---

### 更新分身

更新指定分身的配置。仅传入需要修改的字段。

```
POST {BASE}/api/secondme/avatar/update
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| avatarId | integer | 是 | 分身 ID |
| title | string | 否 | 分身名称 |
| scenarioPrompt | string | 否 | 场景提示词 |
| opening | string | 否 | 开场白 |
| modes | object | 否 | 交互模式配置 |
| distribution | object | 否 | 分发渠道配置 |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/avatar/update" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "avatarId": 3,
    "title": "产品咨询助手 v2",
    "opening": "欢迎！我是升级后的产品顾问，请问有什么可以帮您？"
  }'
```

#### 响应

**成功 (200)**: 返回更新后的完整分身数据（结构同创建响应）。

---

### 删除分身

删除指定的自定义分身。**primary 类型的分身不可删除。**

```
POST {BASE}/api/secondme/avatar/delete
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| avatarId | integer | 是 | 分身 ID |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/avatar/delete" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "avatarId": 3 }'
```

#### 响应

**成功 (200)**

```json
{ "code": 0, "data": null }
```

---

### 设置默认分身

将指定分身设为默认分身。

```
POST {BASE}/api/secondme/avatar/{avatarId}/set-default
```

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| avatarId | integer | 是 | 分身 ID |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/avatar/2/set-default" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{ "code": 0, "data": null }
```

---

### 获取分身公开信息

通过 shareCode 获取分身的公开信息（包含 owner 信息）。

```
GET {BASE}/api/secondme/avatar/public/{shareCode}
```

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| shareCode | string | 是 | 分身分享码 |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/avatar/public/abc123" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "id": 1,
    "shareCode": "abc123",
    "name": "My Avatar",
    "modes": { "textChat": true, "voiceCall": false },
    "interactionCount": 10,
    "viewCount": 50,
    "createdAt": "2026-03-20 10:00:00",
    "ownerUserId": 12345,
    "ownerRoute": "john",
    "ownerUsername": "John",
    "ownerAvatar": "https://..."
  }
}
```

---

### 获取交互记录

获取指定分身的访客交互历史。

```
GET {BASE}/api/secondme/avatar/{avatarId}/interactions
```

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| avatarId | integer | 是 | 分身 ID |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/avatar/2/interactions" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": [
    {
      "id": 1,
      "visitorName": "访客A",
      "messageCount": 15,
      "durationSeconds": 300,
      "summary": "客户咨询了产品价格和功能...",
      "createdAt": "2026-03-28 09:00:00"
    }
  ]
}
```

---

### 创建 API Key

为指定分身创建 API Key。用于开放 API 分发，允许第三方通过 API Key 与分身对话。

```
POST {BASE}/api/secondme/avatar/api-key/create
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| avatarId | integer | 是 | 分身 ID |
| name | string | 是 | 密钥备注名（最长 100 字符） |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/avatar/api-key/create" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "avatarId": 2, "name": "接入官网" }'
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "keyId": 1,
    "avatarId": 2,
    "name": "接入官网",
    "secretKey": "sk-e5443b6842d54208bc2c9a0bc2b65376",
    "enabled": true
  }
}
```

> **Important**: `secretKey` 仅在创建时返回明文，之后不再展示。请提醒用户妥善保存。

---

### 获取 API Key 列表

获取指定分身的所有 API Key。

```
GET {BASE}/api/secondme/avatar/api-key/list
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| avatarId | integer | 是 | 分身 ID |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/avatar/api-key/list?avatarId=2" \
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
        "keyId": 1,
        "avatarId": 2,
        "name": "接入官网",
        "enabled": true
      }
    ]
  }
}
```

---

### 更新 API Key

更新 API Key 的名称或启停状态。

```
POST {BASE}/api/secondme/avatar/api-key/update
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| keyId | integer | 是 | 密钥 ID |
| name | string | 否 | 新的备注名 |
| enabled | boolean | 否 | 是否启用 |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/avatar/api-key/update" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "keyId": 1, "enabled": false }'
```

#### 响应

**成功 (200)**

```json
{ "code": 0, "data": null }
```

---

### 删除 API Key

永久删除指定的 API Key。

```
POST {BASE}/api/secondme/avatar/api-key/delete
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| keyId | integer | 是 | 密钥 ID |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/avatar/api-key/delete" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "keyId": 1 }'
```

#### 响应

**成功 (200)**

```json
{ "code": 0, "data": null }
```

---

## Error Codes

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| auth.scope.missing | 缺少必需的权限（需要 avatar.read 或 avatar.write） |
| avatar.fetch.failed | 获取分身信息失败 |
| avatar.create.failed | 创建分身失败 |
| avatar.update.failed | 更新分身失败 |
| avatar.delete.failed | 删除分身失败 |
| avatar.apikey.failed | API Key 操作失败 |

---

## Share Link

分身的分享链接格式：

```
https://second-me.cn/{ownerRoute}/avatar/{shareCode}
```

- `ownerRoute`: 用户的主页路由（从 `GET {BASE}/api/secondme/user/info` 响应的 `route` 字段获取）
- `shareCode`: 分身的分享码（从创建/详情接口返回）

在展示分身信息时，始终拼接并展示完整的分享链接，而不是只展示 shareCode。

---

## Workflow Guidelines

### 创建分身

引导用户填写以下信息：
1. **title**（必填）: 分身名称，如「产品咨询助手」「新员工培训」
2. **scenarioPrompt**（建议填写）: 场景提示词，描述分身的任务和行为方式
3. **opening**（可选）: 开场白，访客打开时的第一条消息

创建成功后，拼接完整分享链接 `https://second-me.cn/{ownerRoute}/avatar/{shareCode}` 并展示给用户。如果当前上下文中没有用户的 `route`，先调用 `GET {BASE}/api/secondme/user/info` 获取。

### 列表展示

- `type: "primary"` 是默认分身（每用户一个，不可删除），在列表中标注
- `type: "custom"` 是自定义分身，可以编辑和删除
- 每个分身都应展示完整分享链接 `https://second-me.cn/{ownerRoute}/avatar/{shareCode}`

### API Key 管理

- 创建后 **立即** 展示 `secretKey` 并提醒用户保存（仅展示一次）
- 发现用量异常时可以 disable 单个 Key，不影响其他 Key
- 删除 API Key 前需要用户确认

### 删除确认

删除分身或 API Key 前，展示即将删除的对象信息并要求用户明确确认。
