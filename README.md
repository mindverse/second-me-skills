# SecondMe Skills

**用 AI Agent 构建 SecondMe 应用 —— 从想法到上线，一句话搞定。**

SecondMe Skills 是一套 [Claude Code](https://claude.com/claude-code) 技能包，让你通过自然语言对话，快速开发基于 SecondMe API 的全栈应用。无需手动翻文档、写样板代码 —— AI Agent 替你完成从项目初始化、需求定义到代码生成的全流程。

## 你能用它做什么？

- **构建 SecondMe 集成应用**：聊天机器人、智能客服、个性化助手、知识管理工具……任何基于 SecondMe API 的应用
- **入驻 SecondMe AppStore**：优秀作品可在 [SecondMe AppStore](https://app.second.me) 展示，触达真实用户
- **参加月度黑客松**：SecondMe 每月举办一期 Hackathon，已成为 A2A（Agent-to-Agent）领域内最成功的开发者活动之一。查看首届黑客松回顾 → [hackathon.second.me](https://hackathon.second.me)

## 快速开始

### 安装

```bash
npx skills add Mindverse/Second-Me-Skills
```

### 使用

在 Claude Code 中输入：

```bash
/secondme              # 一站式创建项目（推荐）
/secondme --quick      # 快速模式，跳过需求定义，直接生成代码
```

也可以分步执行：

```bash
/secondme-init         # 第 1 步：选择功能模块，初始化项目配置
/secondme-prd          # 第 2 步：通过对话定义产品需求
/secondme-nextjs       # 第 3 步：生成 Next.js 全栈项目
/secondme-reference    # 随时查看 SecondMe API 参考文档
```

## 包含的 Skills

| Skill | 说明 |
|-------|------|
| `/secondme` | 一站式工作流：初始化 → 需求定义 → 项目生成 |
| `/secondme-init` | 初始化项目配置和功能模块选择 |
| `/secondme-prd` | 通过对话式交互定义产品需求 |
| `/secondme-nextjs` | 基于配置和需求生成 Next.js 全栈项目 |
| `/secondme-reference` | SecondMe API 完整技术参考文档 |
| `/secondme-openclaw` | OpenClaw 集成：登录、找人、小镇、发帖，通过 Agent 完成 SecondMe 全流程 |

## 项目结构

```
Second-Me-Skills/
├── README.md
└── skills/
    ├── secondme/              # 一站式工作流
    ├── secondme-init/         # 项目初始化
    ├── secondme-prd/          # 需求定义
    ├── secondme-nextjs/       # Next.js 项目生成
    ├── secondme-reference/    # API 技术参考
    └── secondme-openclaw/     # OpenClaw Agent 集成
```

## 相关链接

- [SecondMe 官网](https://second.me)
- [开发者文档](https://develop-docs.second.me/zh/docs)
- [OAuth2 认证指南](https://develop-docs.second.me/zh/docs/authentication/oauth2)
- [API 参考](https://develop-docs.second.me/zh/docs/api-reference/secondme)
- [首届黑客松](https://hackathon.second.me)

## 许可证

MIT
