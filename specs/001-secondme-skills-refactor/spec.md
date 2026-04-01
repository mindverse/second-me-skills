# Feature Specification: SecondMe Skills 工作流重构

**Feature Branch**: `001-secondme-skills-refactor`
**Created**: 2026-02-05
**Status**: Draft
**Input**: 重构 SecondMe Skills，添加 init、PRD、数据库设计流程，状态管理和模块化支持

## 概述

重构 SecondMe Skills 工作流，引入状态管理机制和功能模块化设计，提供更灵活的开发体验。

### 工作流设计

```
完整流程：
/secondme-init ──> /secondme-prd ──> /secondme-nextjs
   (配置+模块)      (需求对话)         (项目生成)
      │
      └────────── --quick ───────────>  (快速模式，跳过 PRD)
```

### 状态流转

```
[未初始化] ──init──> [已配置] ──prd──> [需求明确] ──nextjs──> [项目就绪]
                        │
                        └──────── quick mode ─────────────────>
```

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 项目初始化与模块选择 (Priority: P1)

开发者希望在开始 SecondMe 项目开发之前，配置好凭证信息，并选择需要的功能模块。系统将配置和选择持久化存储，后续 skills 可以读取。

**Why this priority**: 这是所有后续工作流的基础，同时模块选择决定了后续生成的代码范围。

**Independent Test**: 运行 `/secondme-init`，完成配置和模块选择后，验证 `.secondme/state.json` 已创建且包含正确信息。

**Acceptance Scenarios**:

1. **Given** 开发者首次使用，**When** 运行 `/secondme-init`，**Then** 系统依次收集 OAuth 凭证、数据库连接串，并展示功能模块列表供选择
2. **Given** 开发者选择了功能模块（如 auth + chat），**When** 完成初始化，**Then** `state.json` 记录 stage 为 "init"，modules 包含选中的模块
3. **Given** `state.json` 已存在，**When** 再次运行 `/secondme-init`，**Then** 显示当前配置摘要，允许修改或确认继续

---

### User Story 2 - 需求 PRD 对话式定义 (Priority: P2)

开发者希望通过对话明确产品需求。AI 根据已选模块，针对性地询问相关问题。

**Why this priority**: 明确的需求帮助生成更符合预期的代码，同时 PRD 文档可作为后续参考。

**Independent Test**: 运行 `/secondme-prd`，通过 3-5 轮对话后，`state.json` 的 prd 字段被填充，stage 更新为 "prd"。

**Acceptance Scenarios**:

1. **Given** stage 为 "init" 且已选择 chat 模块，**When** 运行 `/secondme-prd`，**Then** AI 重点询问聊天相关需求（界面风格、历史记录是否保存等）
2. **Given** 开发者描述了需求，**When** AI 确认需求完整，**Then** 更新 `state.json` 的 prd 字段并将 stage 设为 "prd"
3. **Given** stage 不是 "init"，**When** 运行 `/secondme-prd`，**Then** 提示当前状态并询问是否重新定义需求

**前置条件检查**:
- 检查 `.secondme/state.json` 存在
- 检查 stage >= "init"
- 不满足则提示先运行 `/secondme-init`

---

### User Story 3 - Next.js 项目生成 (Priority: P2)

开发者希望基于配置和模块选择，生成完整的 Next.js 项目，包含 OAuth 认证、数据库设计和对应功能代码。

**Why this priority**: 这是最终产出，将之前的配置和设计转化为可运行的代码。

**Independent Test**: 运行 `/secondme-nextjs`，生成的项目可启动并完成 OAuth 登录，数据正确存入数据库。

**Acceptance Scenarios**:

1. **Given** stage 为 "prd" 且选择了 auth + chat 模块，**When** 运行 `/secondme-nextjs`，**Then** 生成包含 User 表、Session 表、登录流程和聊天界面的完整项目
2. **Given** stage 为 "init"，**When** 运行 `/secondme-nextjs --quick`，**Then** 跳过 PRD 检查，使用默认配置生成项目
3. **Given** 项目生成完成，**When** 运行 `npm run dev`，**Then** 项目在 3000 端口启动，OAuth 流程正常工作

**前置条件检查**:
- 检查 `.secondme/state.json` 存在
- 检查 stage >= "prd"（除非使用 --quick 参数）
- 不满足则提示当前状态和建议操作

---

### User Story 4 - 快速模式 (Priority: P3)

开发者希望跳过 PRD 对话，直接从配置生成项目。适用于已经明确需求或快速原型的场景。

**Why this priority**: 提供灵活性，不强制所有开发者都走完整流程。

**Independent Test**: 运行 `/secondme-init` 后直接运行 `/secondme-nextjs --quick`，可以成功生成项目。

**Acceptance Scenarios**:

1. **Given** stage 为 "init"，**When** 运行 `/secondme-nextjs --quick`，**Then** 使用默认 PRD 配置生成项目，不报错
2. **Given** 使用快速模式，**When** 生成项目，**Then** 根据已选模块生成对应功能，PRD 字段保持为空

---

### Edge Cases

- 开发者中途退出 PRD 对话时，已收集的信息应保存到 `state.json`
- 配置文件包含敏感信息，init 完成后提醒将 `.secondme/` 加入 `.gitignore`
- 模块依赖：选择 chat 模块时自动包含 auth 模块
- 数据库连接串格式错误时，提供 PostgreSQL/MySQL/SQLite 的示例格式

---

## 功能模块设计

### 可选模块列表

| 模块 | 说明 | 依赖 | 包含内容 |
|------|------|------|----------|
| `auth` | OAuth 认证 | 无（必选） | User 表核心字段、登录/回调路由 |
| `profile` | 用户信息展示 | auth | User 表扩展字段、个人资料组件 |
| `chat` | 聊天功能 | auth | Session 表、聊天界面、流式响应 |
| `note` | 笔记功能 | auth | 添加笔记 API 路由 |

### 模块与数据库表映射

```
auth 模块（必选）:
└── User 表（核心字段）

profile 模块:
└── User 表（扩展字段）

chat 模块:
└── Session 表
```

---

## 状态文件设计

### `.secondme/state.json` 结构

```json
{
  "version": "1.0",
  "stage": "init | prd | ready",
  "modules": ["auth", "chat"],
  "config": {
    "client_id": "xxx",
    "client_secret": "xxx",
    "redirect_uri": "http://localhost:3000/api/auth/callback",
    "database_url": "postgresql://..."
  },
  "prd": {
    "summary": "应用简介",
    "features": ["功能1", "功能2"],
    "design_preference": "简约现代"
  }
}
```

### Stage 说明

| Stage | 含义 | 可执行操作 |
|-------|------|-----------|
| (无文件) | 未初始化 | 仅 `/secondme-init` |
| `init` | 已配置 | `/secondme-prd` 或 `/secondme-nextjs --quick` |
| `prd` | 需求明确 | `/secondme-nextjs` |
| `ready` | 项目已生成 | 可重新运行任意 skill |

---

## 数据库设计

### User 表（分层设计）

**核心字段（auth 模块，必有）**:

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String | 主键 |
| secondme_user_id | String | SecondMe 用户标识，唯一 |
| access_token | String | 访问令牌 |
| refresh_token | String | 刷新令牌 |
| token_expires_at | DateTime | 令牌过期时间 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

**扩展字段（profile 模块，可选）**:

| 字段 | 类型 | 说明 |
|------|------|------|
| email | String? | 用户邮箱 |
| name | String? | 用户昵称 |
| avatar_url | String? | 头像 URL |

### Session 表（chat 模块）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | String | 主键 |
| user_id | String | 外键 → User |
| secondme_session_id | String | SecondMe 会话标识 |
| title | String? | 会话标题 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

---

## Requirements *(mandatory)*

### Functional Requirements

**状态管理**:
- **FR-001**: 系统 MUST 使用 `.secondme/state.json` 管理项目状态
- **FR-002**: state.json MUST 包含 version、stage、modules、config 字段
- **FR-003**: 每个 skill MUST 在执行前检查前置条件（stage 是否满足）

**初始化 Skill**:
- **FR-004**: `/secondme-init` MUST 收集 OAuth 凭证和数据库连接串
- **FR-005**: `/secondme-init` MUST 展示功能模块列表并支持多选
- **FR-006**: `/secondme-init` MUST 将 auth 模块设为必选
- **FR-007**: 初始化完成后 MUST 提醒将 `.secondme/` 加入 `.gitignore`
- **FR-007a**: `/secondme-init` MUST 创建或更新项目的 `CLAUDE.md`，写入 SecondMe API 文档链接和关键技术参考

**PRD Skill**:
- **FR-008**: `/secondme-prd` MUST 检查 stage >= "init"
- **FR-009**: `/secondme-prd` MUST 根据已选模块针对性提问
- **FR-010**: PRD 完成后 MUST 更新 state.json 的 prd 字段和 stage

**项目生成 Skill**:
- **FR-011**: `/secondme-nextjs` MUST 检查 stage >= "prd"（除非 --quick）
- **FR-012**: `/secondme-nextjs --quick` MUST 允许跳过 PRD 阶段
- **FR-013**: 生成的数据库 Schema MUST 根据已选模块包含对应的表
- **FR-014**: 生成的项目 MUST 包含完整的 OAuth 认证流程
- **FR-015**: 生成的项目 MUST 使用 state.json 中的配置

**API 参考**:
- **FR-016**: Skills SHOULD 引用 SecondMe 官方文档 URL（https://develop-docs.second-me.cn/zh/docs）而非维护独立参考文档

### Key Entities

- **State**: 项目状态，包含当前阶段、已选模块、配置信息、PRD 摘要
- **Module**: 功能模块定义，包含名称、依赖关系、对应的表和组件
- **User**: OAuth 用户，分为核心字段（Token 管理）和扩展字段（个人信息）
- **Session**: 聊天会话，关联用户和 SecondMe 会话

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 开发者可以在 2 分钟内完成 `/secondme-init` 配置和模块选择
- **SC-002**: `/secondme-prd` 对话可以在 5 轮交互内完成需求定义
- **SC-003**: 快速模式下，从 init 到项目可运行不超过 3 分钟
- **SC-004**: 完整模式下，从 init 到项目可运行不超过 8 分钟
- **SC-005**: 生成的数据库 Schema 100% 覆盖所选模块的必需字段
- **SC-006**: 90% 的开发者可以在无额外帮助的情况下完成工作流

---

## Assumptions

- 开发者已在 SecondMe 平台注册应用并获取 OAuth 凭证
- 开发者已安装 Node.js 18+ 和 npm/pnpm
- 开发者有可用的数据库服务（PostgreSQL、MySQL 或 SQLite）
- 项目使用 Next.js 14+ 和 App Router
- 数据库 ORM 使用 Prisma
