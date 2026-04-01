# Quickstart: SecondMe Skills 工作流

**Feature**: 001-secondme-skills-refactor
**Date**: 2026-02-05

## 概述

本指南帮助开发者快速上手 SecondMe Skills 工作流，从零开始创建一个与 SecondMe API 集成的 Next.js 应用。

---

## 前置准备

1. **注册 SecondMe 应用**
   - 访问 SecondMe 开发者后台
   - 创建新应用，获取 Client ID 和 Client Secret
   - 配置回调地址：`http://localhost:3000/api/auth/callback`

2. **准备数据库**
   - PostgreSQL、MySQL 或 SQLite
   - 获取连接串

3. **安装 Claude Code**
   - 确保已安装 Claude Code CLI

---

## 快速开始（3 分钟）

### 方式一：完整流程

```bash
# 1. 初始化配置（约 2 分钟）
/secondme-init

# 2. 定义产品需求（约 3-5 分钟对话）
/secondme-prd

# 3. 生成项目
/secondme-nextjs
```

### 方式二：快速模式

```bash
# 1. 初始化配置
/secondme-init

# 2. 跳过 PRD，直接生成项目
/secondme-nextjs --quick
```

---

## 详细步骤

### Step 1: /secondme-init

运行后，Claude 会询问：

1. **Client ID**: 输入从 SecondMe 获取的 Client ID
2. **Client Secret**: 输入 Client Secret
3. **Redirect URI**: 默认 `http://localhost:3000/api/auth/callback`
4. **Database URL**: 输入数据库连接串
5. **功能模块**: 选择需要的模块
   - ✅ auth (必选) - OAuth 登录
   - ⬜ profile - 用户信息展示
   - ⬜ chat - 聊天功能
   - ⬜ note - 笔记功能

完成后：
- 配置保存到 `.secondme/state.json`
- 创建 `CLAUDE.md`（包含 SecondMe API 文档链接，方便开发时参考）

### Step 2: /secondme-prd (可选)

Claude 会通过对话帮你明确产品需求：

1. 展示已选模块的 API 能力
2. 询问应用要解决的问题
3. 针对模块询问细节
4. 确认设计偏好

完成后，PRD 保存到 `state.json`。

### Step 3: /secondme-nextjs

Claude 根据配置和需求生成完整项目：

```
my-secondme-app/
├── .env.local          # 环境变量（已填充）
├── prisma/
│   └── schema.prisma   # 数据库模型
├── src/
│   └── app/
│       ├── api/
│       │   └── auth/   # OAuth 路由
│       ├── components/ # UI 组件
│       └── page.tsx    # 首页
├── package.json
└── ...
```

### Step 4: 启动项目

```bash
cd my-secondme-app
npm install
npx prisma db push
npm run dev
```

访问 http://localhost:3000，点击登录按钮测试 OAuth 流程。

---

## 功能模块说明

### auth (必选)

包含：
- `/api/auth/login` - 跳转到 SecondMe 授权
- `/api/auth/callback` - OAuth 回调处理
- User 表 - 存储用户 Token
- 登录按钮组件

### profile

包含：
- `/api/user/info` - 获取用户信息
- User 表扩展字段 - email, name, avatar_url
- 个人资料展示组件

### chat

包含：
- `/api/chat` - 流式对话 API
- `/api/sessions` - 会话历史 API
- Session 表 - 存储会话记录
- 聊天界面组件

### note

包含：
- `/api/note` - 添加笔记 API

---

## 常见问题

### Q: 如何修改配置？

重新运行 `/secondme-init`，会显示当前配置并允许修改。

### Q: 如何查看 API 参考？

查看项目根目录的 `CLAUDE.md` 文件，或直接访问 [SecondMe 官方文档](https://develop-docs.second-me.cn/zh/docs)。

### Q: 项目生成后如何添加新功能？

1. 修改 `.secondme/state.json` 中的 modules
2. 重新运行 `/secondme-nextjs`
3. 或手动添加代码

### Q: 敏感信息安全吗？

`.secondme/` 目录包含 OAuth 凭证，请确保：
- 已添加到 `.gitignore`
- 不要提交到版本控制

---

## 下一步

- 阅读 [SecondMe API 文档](https://develop-docs.second-me.cn/zh/docs)
- 使用 `/frontend-design` 优化界面设计
- 部署到生产环境
