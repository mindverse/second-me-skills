# SecondMe Skills

**SecondMe Skills 包含两类能力：给开发者构建基于 SecondMe 的第三方应用，也给终端用户通过 Agent 直接使用 SecondMe。**

SecondMe Skills 是一套技能包，当前主要覆盖两条使用路径：

- **开发者技能**：面向想基于 SecondMe API 开发第三方应用的开发者，帮助完成初始化、需求定义、代码生成和 API 参考查阅
- **Agent 使用技能**：面向想通过 OpenClaw / Agent 直接登录和使用 SecondMe 的用户，覆盖登录、资料、Plaza 只读、Discover、Key Memory、Activity 和第三方技能目录等场景

## 你能用它做什么？

### 面向开发者

- 用自然语言快速生成基于 SecondMe API 的应用
- 初始化 OAuth、数据库、模块配置
- 通过对话定义 PRD，再生成 Next.js 全栈项目
- 从现有项目构建 SecondMe Skill / MCP 集成，并补齐发布所需 manifest
- 为 MCP 服务补齐 bearer token 鉴权、用户映射和远程工具暴露
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

### 1. 安装仓库技能

```bash
npx skills add Mindverse/Second-Me-Skills
```

### 2. 开发者用法

在 Claude Code 中输入：

```bash
/secondme
/secondme --quick
```

也可以分步执行：

```bash
/secondme-init
/secondme-prd
/secondme-nextjs
/secondme-reference
```

如果你已经有一个本地项目，想把它发布成 SecondMe Skill / MCP 集成，也可以使用仓库里的 `secondme-app-build-skill`。

实现这类 MCP 服务时，需要特别注意：

- SecondMe 在调用 MCP 时会通过 `Authorization` header 传入当前用户的 `accessToken`
- 应用服务端需要用这个 token 识别当前 SecondMe 用户，而不是把它当成普通静态 API key
- 推荐做法是先调用 `user/info` 获取上游用户身份，再映射或 upsert 到本地用户表，然后用本地用户上下文执行业务

### 3. OpenClaw / Agent 用法

如果你的 Agent 支持从 GitHub repo/path 安装技能，可以安装 `openclaw/` 下的统一 SecondMe 技能：

- `openclaw/secondme`

安装后，用户可以直接通过 Agent 发起 SecondMe 相关操作，例如：

- `登录 SecondMe`
- `帮我看看资料`
- `看看今天都有哪些动态`
- `看看推荐用户`
- `帮我查一下 Key Memory`
- `看看有哪些外部技能可以装`
- `从远端技能目录里找一个能装的技能`

## 包含的 Skills

### 开发者技能

| Skill | 说明 |
|-------|------|
| `/secondme` | 一站式工作流：初始化 → 需求定义 → 项目生成 |
| `/secondme-init` | 初始化项目配置和功能模块选择 |
| `/secondme-prd` | 通过对话式交互定义产品需求 |
| `/secondme-nextjs` | 基于配置和需求生成 Next.js 全栈项目 |
| `secondme-app-build-skill` | 从现有项目构建或更新 SecondMe Skill / MCP 集成，并指导 MCP 服务实现 |
| `/secondme-reference` | SecondMe API 完整技术参考文档 |

### OpenClaw / Agent 使用技能

| Skill | 说明 |
|-------|------|
| `secondme` | 登录、资料、Plaza 只读、Discover、Key Memory、Activity 和第三方技能管理的统一 OpenClaw 技能 |

## 项目结构

```text
Second-Me-Skills/
├── README.md
├── skills/
│   ├── secondme/              # 一站式开发者工作流
│   ├── secondme-init/         # 项目初始化
│   ├── secondme-prd/          # 需求定义
│   ├── secondme-nextjs/       # Next.js 项目生成
│   └── secondme-reference/    # API 技术参考
├── openclaw/
│   └── secondme/              # 登录、资料、Plaza 只读、Discover、Key Memory、Activity、第三方技能
└── docs/
    └── superpowers/           # 设计和计划文档
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
