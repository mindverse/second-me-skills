# Data Model: SecondMe Skills 工作流重构

**Feature**: 001-secondme-skills-refactor
**Date**: 2026-02-05

## 概述

本文档定义 SecondMe Skills 工作流中使用的数据模型，包括状态文件结构、功能模块定义、以及生成的数据库表结构。

---

## 1. 状态文件 (state.json)

### 完整结构

```typescript
interface SecondMeState {
  // 版本号，用于未来兼容性迁移
  version: "1.0";

  // 当前阶段
  stage: "init" | "prd" | "ready";

  // 应用名称（用作项目目录名）
  app_name: string;

  // 已选择的功能模块
  modules: Module[];

  // OAuth 和数据库配置
  config: {
    client_id: string;
    client_secret: string;
    redirect_uri: string;           // 开发用（localhost）
    redirect_uris?: string[];       // 所有回调地址
    database_url: string;
    allowed_scopes?: string[];      // App Info 中的权限列表
  };

  // API 端点配置（由 init 自动生成，不需要用户输入）
  api: {
    base_url: string;                // "https://api.mindverse.com/gate/lab"
    oauth_url: string;               // "https://go.second.me/oauth/"
    token_endpoint: string;          // base_url + "/api/oauth/token"
    access_token_ttl: number;        // 7200（2 小时）
    refresh_token_ttl: number;       // 2592000（30 天）
  };

  // 官方文档链接（由 init 自动生成）
  docs: {
    quickstart: string;
    oauth2: string;
    api_reference: string;
    errors: string;
  };

  // PRD 对话结果（可选）
  prd?: {
    summary: string;
    features: string[];
    target_users?: string;
    design_preference?: string;
  };
}

type Module = "auth" | "profile" | "chat" | "note";
```

### 阶段转换规则

| 当前阶段 | 触发操作 | 新阶段 |
|----------|----------|--------|
| (不存在) | /secondme-init 完成 | init |
| init | /secondme-prd 完成 | prd |
| init | /secondme-nextjs --quick | ready |
| prd | /secondme-nextjs 完成 | ready |
| ready | 任意 skill 重新运行 | 可重置 |

### 示例

```json
{
  "version": "1.0",
  "stage": "prd",
  "app_name": "secondme-tinder",
  "modules": ["auth", "chat", "profile"],
  "config": {
    "client_id": "71658da7-659c-414a-abdf-cb6472037fc2",
    "client_secret": "your-secret-here",
    "redirect_uri": "http://localhost:3000/api/auth/callback",
    "redirect_uris": [
      "http://localhost:3000/api/auth/callback",
      "https://2026-02-04-secondme-tinder.vercel.app/api/auth/callback",
      "https://tinder.second.me/api/auth/callback"
    ],
    "database_url": "postgresql://user:pass@localhost:5432/myapp",
    "allowed_scopes": ["userinfo", "chat.read", "chat.write", "note.write", "voice", "plaza.read", "plaza.write", "friend.read", "friend.write", "discover", "memory.read", "memory.write", "activity", "developer"]
  },
  "api": {
    "base_url": "https://api.mindverse.com/gate/lab",
    "oauth_url": "https://go.second.me/oauth/",
    "token_endpoint": "https://api.mindverse.com/gate/lab/api/oauth/token",
    "access_token_ttl": 7200,
    "refresh_token_ttl": 2592000
  },
  "docs": {
    "quickstart": "https://develop-docs.second.me/zh/docs",
    "oauth2": "https://develop-docs.second.me/zh/docs/authentication/oauth2",
    "api_reference": "https://develop-docs.second.me/zh/docs/api-reference/secondme",
    "errors": "https://develop-docs.second.me/zh/docs/errors"
  },
  "prd": {
    "summary": "AI 聊天助手应用",
    "features": [
      "用户通过 SecondMe 登录",
      "与 AI 进行流式对话",
      "保存并查看历史会话"
    ],
    "target_users": "希望与 AI 聊天的用户",
    "design_preference": "简约现代，亮色主题"
  }
}
```

---

## 2. 功能模块定义

### Module 枚举

| 模块 ID | 名称 | 必选 | 依赖 | 描述 |
|---------|------|------|------|------|
| `auth` | OAuth 认证 | 是 | 无 | 用户登录、Token 管理 |
| `profile` | 用户信息 | 否 | auth | 展示用户资料 |
| `chat` | 聊天功能 | 否 | auth | 与 SecondMe AI 对话 |
| `note` | 笔记功能 | 否 | auth | 添加笔记到用户记忆 |

### 模块依赖解析

```
用户选择: [chat]
解析后:   [auth, chat]  // auth 自动添加

用户选择: [profile, note]
解析后:   [auth, profile, note]  // auth 自动添加
```

### Scopes 到模块的自动映射

当用户提供 App Info 格式时，根据 `Allowed Scopes` 自动推断模块：

| Scope | 映射模块 |
|-------|----------|
| `userinfo` | `auth`（必选） |
| `chat.read` | `chat` |
| `chat.write` | `chat` |
| `note.write` | `note` |
| `voice` | 记录但暂不生成代码 |
| `plaza.read` | `plaza` |
| `plaza.write` | `plaza` |
| `friend.read` | `friend` |
| `friend.write` | `friend` |
| `discover` | `discover` |
| `memory.read` | `memory` |
| `memory.write` | `memory` |
| `activity` | `activity` |
| `developer` | `developer` |

**示例**：

```
Allowed Scopes: userinfo, chat.read, chat.write, note.write
推断模块: [auth, chat, note]
```

### 模块 → 数据库表映射

| 模块 | 生成的表 | 字段范围 |
|------|----------|----------|
| auth | User | 核心字段 |
| profile | User | 扩展字段 |
| chat | User, Session | 全部 |
| note | User | 核心字段 |

---

## 3. 数据库表结构

### User 表

#### 核心字段 (auth 模块)

```prisma
model User {
  id                String   @id @default(cuid())
  secondmeUserId    String   @unique @map("secondme_user_id")
  accessToken       String   @map("access_token")
  refreshToken      String   @map("refresh_token")
  tokenExpiresAt    DateTime @map("token_expires_at")
  createdAt         DateTime @default(now()) @map("created_at")
  updatedAt         DateTime @updatedAt @map("updated_at")

  @@map("users")
}
```

#### 扩展字段 (profile 模块)

```prisma
model User {
  // ... 核心字段 ...

  email             String?
  name              String?
  avatarUrl         String?  @map("avatar_url")
  route             String?
}
```

#### 关联关系 (chat 模块)

```prisma
model User {
  // ... 核心字段 + 扩展字段 ...

  sessions          Session[]
}
```

### Session 表 (chat 模块)

```prisma
model Session {
  id                  String   @id @default(cuid())
  userId              String   @map("user_id")
  secondmeSessionId   String   @map("secondme_session_id")
  title               String?
  createdAt           DateTime @default(now()) @map("created_at")
  updatedAt           DateTime @updatedAt @map("updated_at")

  user                User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("sessions")
}
```

---

## 4. 完整 Schema 示例

### 仅 auth 模块

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id                String   @id @default(cuid())
  secondmeUserId    String   @unique @map("secondme_user_id")
  accessToken       String   @map("access_token")
  refreshToken      String   @map("refresh_token")
  tokenExpiresAt    DateTime @map("token_expires_at")
  createdAt         DateTime @default(now()) @map("created_at")
  updatedAt         DateTime @updatedAt @map("updated_at")

  @@map("users")
}
```

### auth + profile + chat 模块

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id                String   @id @default(cuid())
  secondmeUserId    String   @unique @map("secondme_user_id")
  accessToken       String   @map("access_token")
  refreshToken      String   @map("refresh_token")
  tokenExpiresAt    DateTime @map("token_expires_at")

  // profile 模块字段
  email             String?
  name              String?
  avatarUrl         String?  @map("avatar_url")
  route             String?

  createdAt         DateTime @default(now()) @map("created_at")
  updatedAt         DateTime @updatedAt @map("updated_at")

  // chat 模块关联
  sessions          Session[]

  @@map("users")
}

model Session {
  id                  String   @id @default(cuid())
  userId              String   @map("user_id")
  secondmeSessionId   String   @map("secondme_session_id")
  title               String?
  createdAt           DateTime @default(now()) @map("created_at")
  updatedAt           DateTime @updatedAt @map("updated_at")

  user                User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("sessions")
}
```

---

## 5. 验证规则

### state.json 验证

| 字段 | 规则 |
|------|------|
| version | 必须为 "1.0" |
| stage | 必须为 init/prd/ready 之一 |
| app_name | 非空字符串，用作项目目录名 |
| modules | 必须包含 "auth" |
| config.client_id | 非空字符串 |
| config.client_secret | 非空字符串，不能为占位符 |
| config.redirect_uri | 有效 URL 格式 |
| config.redirect_uris | URL 数组（可选） |
| config.database_url | 有效数据库连接串格式 |
| config.allowed_scopes | 字符串数组（可选） |
| api.base_url | 有效 URL 格式 |
| api.oauth_url | 有效 URL 格式 |
| api.token_endpoint | 有效 URL 格式 |
| api.access_token_ttl | 正整数（秒） |
| api.refresh_token_ttl | 正整数（秒） |
| docs.quickstart | 有效 URL 格式 |
| docs.oauth2 | 有效 URL 格式 |
| docs.api_reference | 有效 URL 格式 |
| docs.errors | 有效 URL 格式 |

### 数据库连接串格式

| 数据库 | 格式示例 |
|--------|----------|
| PostgreSQL | `postgresql://user:pass@host:5432/db` |
| MySQL | `mysql://user:pass@host:3306/db` |
| SQLite | `file:./dev.db` |
