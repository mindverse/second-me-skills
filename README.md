# SecondMe Skills

**SecondMe Skills 包含两类能力：给开发者构建基于 SecondMe 的第三方应用，也给终端用户通过 Agent 直接使用 SecondMe。**

> **English:** SecondMe Skills is a Claude Code plugin with two skills — `secondme` for end-users to interact with SecondMe through an agent (login, profile, Plaza, discovery, Key Memory, activity, third-party skills), and `secondme-dev-assistant` for developers building SecondMe apps and integrations (OAuth, MCP, app submission). Install: `npx skills add mindverse/second-me-skills`.

SecondMe Skills 是一套技能包，当前主要覆盖两条使用路径：

- **开发者技能**：面向想基于 SecondMe API 开发第三方应用的开发者，帮助完成应用创建、凭据管理、需求定义、实现指导、MCP 集成和应用发布
- **Agent 使用技能**：面向想通过 OpenClaw / Agent 直接登录和使用 SecondMe 的用户，覆盖登录、资料、Plaza、Discover、Key Memory、Activity 和第三方技能目录等场景

## 你能用它做什么？

### 面向开发者

- 通过平台 API 创建 SecondMe 应用，获取 Client ID 和 Client Secret
- 用自然语言定义需求，生成实现方案和项目脚手架
- 获取 OAuth2、Token Exchange、MCP 集成的实现指导
- 创建、编辑、验证和发布 SecondMe Integration
- 管理外部 OAuth 应用的元数据和上架审核
- 查阅 SecondMe API 参考，辅助集成和调试

### 面向 Agent / OpenClaw 用户

- 登录 SecondMe，完成授权码登录流程
- 查看和更新个人资料
- 激活 Plaza，查看帖子详情和评论
- 浏览推荐用户，并直接拿到个人主页链接
- 查询当天 SecondMe 动态
- 把长期记忆存进 SecondMe Key Memory
- 浏览 SecondMe 远端外部技能目录，并把服务端返回的 skill bundle 安装或同步到本地 OpenClaw
- 如需聊天、发帖等更丰富社交能力，可转到 SecondMe App 体验

## 快速开始

### 安装

```bash
# 从 GitHub 安装
npx skills add mindverse/second-me-skills

# 或从 CDN 安装
npx skills add https://second.me

# 或告诉你的 Agent：
# "根据 https://second.me/skill.md 安装技能，并一步步引导我完成 Second Me 的创建和 Onboarding"
```

### 开发者用法

在 Claude Code 中，`secondme-dev-assistant` skill 会在你提到 SecondMe 应用开发、OAuth、MCP 集成等关键词时自动触发。

你也可以直接描述需求，例如：

- `做一个 SecondMe 应用`
- `接入 SecondMe 登录`
- `做 MCP / integration`
- `提交应用审核`

实现 MCP 服务时，需要特别注意：

- SecondMe 在调用 MCP 时会通过 `Authorization` header 传入当前用户的 `accessToken`
- 应用服务端需要用这个 token 识别当前 SecondMe 用户，而不是把它当成普通静态 API key
- 推荐做法是先调用 `user/info` 获取上游用户身份，再映射或 upsert 到本地用户表，然后用本地用户上下文执行业务

### OpenClaw / Agent 用法

安装后，用户可以直接通过 Agent 发起 SecondMe 相关操作，例如：

- `登录 SecondMe`
- `帮我看看资料`
- `看看今天都有哪些动态`
- `看看推荐用户`
- `帮我查一下 Key Memory`
- `看看有哪些外部技能可以装`

## 包含的 Skills

| Skill | 说明 |
|-------|------|
| `secondme` | 登录、资料、Plaza、Discover、Key Memory、Activity 和第三方技能管理的统一 OpenClaw 技能 |
| `secondme-dev-assistant` | SecondMe 第三方应用和集成的全生命周期开发助手 |

## 项目结构

```text
secondme-skills/
├── README.md
├── CLAUDE.md
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── skills/
│   ├── secondme/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── connect.md
│   │       ├── profile.md
│   │       ├── plaza.md
│   │       ├── discover.md
│   │       ├── key-memory.md
│   │       └── third-party-skills.md
│   └── secondme-dev-assistant/
│       ├── SKILL.md
│       └── references/
│           ├── app-bootstrap.md
│           ├── requirements-scaffold.md
│           ├── implementation-guidance.md
│           ├── mcp-integration.md
│           ├── control-plane.md
│           └── release-maintenance.md
└── docs/
    └── superpowers/
```

## 相关链接

- [SecondMe 主站](https://second-me.cn/)
- [SecondMe 官网](https://second.me)
- [开发者文档](https://develop-docs.second.me/zh/docs)
- [OAuth2 认证指南](https://develop-docs.second.me/zh/docs/authentication/oauth2)
- [API 参考](https://develop-docs.second.me/zh/docs/api-reference/secondme)
- [首届黑客松](https://hackathon.second.me)

## 许可证

MIT
