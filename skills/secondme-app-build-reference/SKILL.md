---
name: secondme-reference
description: SecondMe API 技术参考文档，供开发时查阅
user-invocable: true
---

# SecondMe API 技术参考

本文档包含 SecondMe API 的完整技术参考信息，供开发时查阅。

---

## API 基础 URL

```
https://api.mindverse.com/gate/lab
```

---

## OAuth2 授权 URL

```
https://go.second.me/oauth/
```

---

## OAuth2 流程

```
1. 用户点击登录 → 跳转到 SecondMe 授权页面
2. 用户授权 → 重定向回你的应用（带 authorization_code）
3. 后端用 code 换取 access_token 和 refresh_token
4. 使用 access_token 调用 SecondMe API
5. Token 过期时使用 refresh_token 刷新
```

---

## 授权 URL 构造

**重要：`oauth_url` 已包含完整路径，直接在后面拼接 `?` 和查询参数即可，不要追加 `/authorize` 等路径。**

```typescript
const OAUTH_URL = 'https://go.second.me/oauth/';

const params = new URLSearchParams({
  client_id: process.env.SECONDME_CLIENT_ID,
  redirect_uri: process.env.SECONDME_REDIRECT_URI,
  response_type: 'code',
  state: generatedState,
});

// ✅ 正确：直接拼接 ? 和参数
const authUrl = `${OAUTH_URL}?${params.toString()}`;
// 结果: https://go.second.me/oauth/?client_id=...&redirect_uri=...

// ❌ 错误：不要追加 /authorize 等路径
// const authUrl = `${OAUTH_URL}/authorize?${params}`;
// 会变成: https://go.second.me/oauth//authorize?... ❌
```

---

## Token 交换（用授权码换 Token）

### 端点

```
POST {base_url}/api/oauth/token/code
```

### 请求格式

**Content-Type 必须是 `application/x-www-form-urlencoded`，不是 JSON。**

```typescript
const response = await fetch(`${API_BASE_URL}/api/oauth/token/code`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',  // 必须
  },
  body: new URLSearchParams({
    grant_type: 'authorization_code',
    code: authorizationCode,
    redirect_uri: process.env.SECONDME_REDIRECT_URI,
    client_id: process.env.SECONDME_CLIENT_ID,
    client_secret: process.env.SECONDME_CLIENT_SECRET,
  }),
});
```

### 响应格式

**响应遵循统一包装格式，字段使用 camelCase（不是 OAuth2 标准的 snake_case）：**

```json
{
  "code": 0,
  "data": {
    "accessToken": "lba_at_xxxxx...",
    "refreshToken": "lba_rt_xxxxx...",
    "tokenType": "Bearer",
    "expiresIn": 7200,
    "scope": ["user.info", "chat"]
  }
}
```

### 响应处理

```typescript
const result = await response.json();

// 必须检查 code 字段
if (result.code !== 0 || !result.data) {
  throw new Error(`Token exchange failed: ${result.message}`);
}

// 从 data 中提取，使用 camelCase
const { accessToken, refreshToken, expiresIn } = result.data;
```

---

## Token 刷新

### 端点

```
POST {base_url}/api/oauth/token/refresh
```

### 请求格式

```typescript
const response = await fetch(`${API_BASE_URL}/api/oauth/token/refresh`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    grant_type: 'refresh_token',
    refresh_token: storedRefreshToken,
    client_id: process.env.SECONDME_CLIENT_ID,
    client_secret: process.env.SECONDME_CLIENT_SECRET,
  }),
});
```

响应格式与 Token 交换一致。

---

## Token 有效期

| Token 类型 | 前缀 | 有效期 |
|-----------|------|--------|
| 授权码 | `lba_ac_` | 5 分钟 |
| Access Token | `lba_at_` | 2 小时 |
| Refresh Token | `lba_rt_` | 30 天 |

---

## MCP Bearer Token 与用户解析

如果 SecondMe 以用户态调用你的 MCP，平台会在 MCP 请求的 `Authorization` header 中传入当前用户的 access token：

```http
Authorization: Bearer <accessToken>
```

这个 token 不是静态应用密钥，而是当前触发 MCP 的 SecondMe 用户身份。

推荐实现方式参考 `SemeCompat`：

1. MCP 服务端或 API 路由读取 `Authorization` header
2. 解析出 bearer token，缺失或格式错误时直接返回 `401`
3. 用该 token 调用上游 `user/info` 接口识别当前 SecondMe 用户
4. 用上游用户 id 映射到本地 `users.oauth_id` 或等价外部 id
5. 查不到时自动 upsert 本地用户
6. 用解析出的本地 `user.id` 执行业务逻辑

### 推荐分层

- App API 层：负责 bearer token 鉴权、解析 SecondMe 用户、映射本地用户、校验资源归属
- MCP server / transport 层：负责 MCP tool 暴露和把 `Authorization` header 原样透传到站内 API
- 业务服务层：只接收已解析的本地用户 id，不直接处理 bearer token

### Bearer Token 读取示例

```typescript
function readBearerToken(request: Request): string | null {
  const header = request.headers.get('authorization');
  if (!header?.startsWith('Bearer ')) {
    return null;
  }
  return header.slice('Bearer '.length).trim() || null;
}
```

### 本地用户解析流程示例

```typescript
export async function requireApiAuth(request: Request): Promise<AuthUser> {
  const accessToken = readBearerToken(request);
  if (!accessToken) {
    throw new Error('UNAUTHORIZED');
  }

  const userInfo = await getUserInfo(accessToken);
  const user = await upsertUserByOauthProfile({
    oauthId: userInfo.id,
    nickname: userInfo.nickname,
    avatar: userInfo.avatar || null,
    accessToken,
  });

  return toAuthUser(user);
}
```

### MCP Server 透传示例

```typescript
const authorization = request.headers.authorization || null;
await authStorage.run({ authorization }, async () => {
  await transport.handleRequest(request, response, parsedBody);
});
```

如果 MCP server 再去调用站内 HTTP API，继续透传这个 header：

```typescript
await fetch(`${baseUrl}/api/mcp/compat/random`, {
  method: 'POST',
  headers: {
    Authorization: accessToken,
    Accept: 'application/json',
  },
});
```

### 常见实现错误

- 把 bearer token 当成全局 API key 使用，没有解析当前用户
- 直接在 MCP server 里访问数据库，绕过应用现有鉴权和资源归属检查
- 没有把上游用户映射到本地用户，导致业务层拿不到稳定的本地 user id
- token 无效时返回 `500`，而不是明确的 `401`
- 查询他人资源时没有做用户归属校验

### 推荐错误码

| 场景 | 推荐状态码 |
|------|-----------|
| token 缺失或无效 | `401` |
| 资源不属于当前用户 | `403` |
| 目标资源不存在 | `404` |
| 输入不合法 | `400` |
| 其他未处理异常 | `500` |

### 推荐测试项

- bearer token 缺失时拒绝请求
- bearer token 无效时映射为 `401`
- 现有上游用户能够解析并同步最新 access token
- 新上游用户能够自动 upsert 到本地用户表
- MCP server 调用站内 API 时会原样透传 `Authorization`
- 资源归属错误时返回 `403`

---

## 权限列表（Scopes）

| 权限 | 说明 |
|------|------|
| `user.info` | 用户基础信息 |
| `user.info.shades` | 用户兴趣标签 |
| `user.info.softmemory` | 用户软记忆 |
| `note.add` | 添加笔记 |
| `chat` | 聊天功能 |
| `chat` | 结构化动作判断（Act） |

---

## API 响应格式与处理

**重要：所有 SecondMe API 响应都遵循统一格式：**

```json
{
  "code": 0,
  "data": { ... }  // 实际数据在 data 字段内
}
```

**前端代码必须正确提取数据：**

```typescript
// 注意：以下 /api/secondme/... 是 Next.js 本地路由（由 secondme-nextjs skill 生成），
// 本地路由会代理请求到上游 SecondMe API，并透传上游的响应格式。

// ❌ 错误写法 - 直接使用响应会导致 .map is not a function
const response = await fetch('/api/secondme/user/shades');  // Next.js 本地路由
const shades = await response.json();
shades.map(item => ...)  // 错误！

// ✅ 正确写法 - 提取 data 字段内的数据
const response = await fetch('/api/secondme/user/shades');  // Next.js 本地路由
const result = await response.json();
if (result.code === 0) {
  const shades = result.data.shades;  // 正确！
  shades.map(item => ...)
}
```

---

## 各 API 的数据路径

> 以下路径均为上游 SecondMe API 路径，完整 URL = `{base_url}/api/secondme{path}`
> 其中 `base_url` 来自 `state.api.base_url`（默认 `https://api.mindverse.com/gate/lab`）

| 上游 API 路径 | 数据路径 | 类型 |
|--------------|---------|------|
| `/api/secondme/user/info` | `result.data` | object（含 email, name, avatarUrl, route 等字段） |
| `/api/secondme/user/shades` | `result.data.shades` | array |
| `/api/secondme/user/softmemory` | `result.data.list` | array |
| `/api/secondme/chat/session/list` | `result.data.sessions` | array |
| `/api/secondme/chat/session/messages` | `result.data.messages` | array |
| `/api/secondme/act/stream` | SSE 流式 JSON（需拼接 delta） | SSE stream |
| `/api/secondme/note/add` | `result.data.noteId` | number |
| `/api/secondme/agent_memory/ingest` | `result.data.eventId` / `result.data.isDuplicate` | object |

---

## Act API（结构化动作判断）

Act API 是独立于 Chat API 的接口，约束模型仅输出合法 JSON 对象，适用于情感分析、意图分类等结构化决策场景。权限使用 `chat` scope。

### 端点（上游 API）

```
POST {base_url}/api/secondme/act/stream
```

### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| message | string | 是 | 用户消息内容 |
| actionControl | string | 是 | 动作控制说明（20-8000 字符），定义 JSON 结构与判断规则 |
| appId | string | 否 | 应用 ID |
| sessionId | string | 否 | 会话 ID，不提供则自动生成 |
| systemPrompt | string | 否 | 系统提示词，仅新会话首次有效 |

### actionControl 示例

```
仅输出合法 JSON 对象，不要解释。
输出结构：{"is_liked": boolean}。
当用户明确表达喜欢或支持时 is_liked=true，否则 is_liked=false。
```

### 响应格式（SSE）

```
event: session
data: {"sessionId": "labs_sess_xxx"}

data: {"choices": [{"delta": {"content": "{\"is_liked\": true}"}}]}

data: [DONE]
```

### 前端处理示例

```typescript
// 调用 Act API 进行结构化判断（通过 Next.js 本地路由代理到上游）
const response = await fetch('/api/secondme/act/stream', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: userMessage,
    actionControl: '仅输出合法 JSON。结构：{"intent": "like"|"dislike"|"neutral"}。根据用户表达判断意图。信息不足时返回 {"intent": "neutral"}。'
  })
});

// 拼接 SSE 流中的 delta content，最终 JSON.parse 得到结果
```

### Chat vs Act 使用场景

| 场景 | 使用 API | 原因 |
|------|---------|------|
| 自由对话 | `/chat/stream` | 返回自然语言文本 |
| 情感/意图判断 | `/act/stream` | 返回结构化 JSON |
| 是/否决策 | `/act/stream` | 返回 `{"result": boolean}` |
| 多分类判断 | `/act/stream` | 返回 `{"category": "..."}` |
| 内容生成 | `/chat/stream` | 需要长文本输出 |

---

## Agent Memory API（事件上报与查询）

Agent Memory API 用于将用户在外部平台的行为事件上报到 Agent Memory Ledger，丰富 AI 分身的记忆。认证方式与其他 SecondMe API 一致（OAuth2 Token），**不需要特定 scope**。

### 上报端点

```
POST {base_url}/api/secondme/agent_memory/ingest
```

### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| channel | ChannelInfo | 是 | 频道信息 |
| action | string | 是 | 动作类型 |
| refs | RefItem[] | 是 | 证据指针数组（至少 1 项） |
| actionLabel | string | 否 | 动作展示文案 |
| displayText | string | 否 | 用户可读摘要 |
| eventDesc | string | 否 | 开发者描述 |
| eventTime | integer | 否 | 事件时间戳(毫秒) |
| importance | number | 否 | 重要性 0.0~1.0 |
| idempotencyKey | string | 否 | 幂等键 |
| payload | object | 否 | 扩展信息 |

### 嵌套类型

**ChannelInfo**: `{ kind: string, id?: string, url?: string, meta?: object }`

> `platform` 由服务端根据应用 Client ID 自动填充，前端无需传入。

**RefItem**: `{ objectType: string, objectId: string, type?: string, url?: string, contentPreview?: string, snapshot?: RefSnapshot }`

**RefSnapshot**: `{ text: string, capturedAt?: number, hash?: string }`

### 幂等键生成规则

前端应生成幂等键防止重复上报（参照 plaza 前端实现）：

```typescript
// 规则: sha256("external:" + objectType + ":" + objectId)
// 注意：platform 和 userId 由后端自动填充，前端无需关心
import { sha256 } from 'some-hash-lib';

function generateIdempotencyKey(objectType: string, objectId: string): string {
  return sha256(`external:${objectType}:${objectId}`);
}
```

### 常见 action 类型

| action | 说明 | 典型场景 |
|--------|------|---------|
| `post_created` | 发帖 | 用户在广场发布新帖子 |
| `reply` | 回帖 | 用户回复某个帖子 |
| `ai_reply` | AI 回帖 | AI 分身自动回复帖子 |
| `find_people` | 找人 | 用户搜索其他用户 |
| `replied` | 被回帖 | 用户的帖子被他人回复 |
| `post_viewed` | 看帖 | 用户浏览帖子 |
| `user_liked` | 点赞 | 用户点赞某内容 |
| `liked` | 被赞 | 用户的内容被他人点赞 |

### 响应格式

```json
{
  "code": 0,
  "data": {
    "eventId": 123,
    "isDuplicate": false
  }
}
```

### 前端集成示例（TypeScript）

```typescript
interface ChannelInfo {
  kind: string;
  id?: string;
  url?: string;
  meta?: Record<string, unknown>;
}

interface RefItem {
  objectType: string;
  objectId: string;
  type?: string;
  url?: string;
  contentPreview?: string;
  snapshot?: { text: string; capturedAt?: number; hash?: string };
}

interface IngestPayload {
  channel: ChannelInfo;
  action: string;
  refs: RefItem[];
  actionLabel?: string;
  displayText?: string;
  eventTime?: number;
  importance?: number;
  idempotencyKey?: string;
  payload?: Record<string, unknown>;
}

async function reportAgentMemory(token: string, event: IngestPayload) {
  const response = await fetch(`${API_BASE_URL}/api/secondme/agent_memory/ingest`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(event),
  });
  const result = await response.json();
  if (result.code !== 0) {
    throw new Error(`Ingest failed: ${result.message}`);
  }
  return result.data; // { eventId: number, isDuplicate: boolean }
}
```

### 错误码

| 错误码 | HTTP | 说明 |
|-------|------|------|
| `agent_memory.write.disabled` | 403 | 用户的 Agent Memory 写入已禁用 |
| `agent_memory.ingest.failed` | 502 | 上报失败 |

---

## 开发注意事项

### State 参数

**直接忽略 `state` 参数验证。** 在回调处理时不需要验证 state，直接处理授权码即可。

### CSS @import 规则顺序

**重要：** 在 CSS 文件中，`@import` 语句必须放在文件的最开头（只能在 `@charset` 和 `@layer` 之后）。如果在其他 CSS 规则之后使用 `@import`，会导致解析错误。

```css
/* 正确写法 - @import 放在最前面 */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC&display=swap');

:root {
  --primary-color: #000;
}

/* 错误写法 - @import 不能放在其他规则之后 */
:root {
  --primary-color: #000;
}
@import url('...'); /* 这会报错！ */
```

---

## 官方文档链接

| 文档 | 地址 |
|------|------|
| 快速入门 | https://develop-docs.second.me/zh/docs |
| 认证概述 | https://develop-docs.second.me/zh/docs/authentication |
| OAuth2 指南 | https://develop-docs.second.me/zh/docs/authentication/oauth2 |
| SecondMe API 参考 | https://develop-docs.second.me/zh/docs/api-reference/secondme |
| OAuth2 API 参考 | https://develop-docs.second.me/zh/docs/api-reference/oauth |
| 错误码参考 | https://develop-docs.second.me/zh/docs/errors |
