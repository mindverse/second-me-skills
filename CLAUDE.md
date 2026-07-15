# secondme-skills Development Guidelines

## Project Structure

```text
skills/
  secondme/                       # 用户 skill（登录、资料、Plaza、Discover、Key Memory、Activity、第三方技能）
    SKILL.md                      # 概览和路由（< 500 行）
    references/                   # 详细参考文档（按需加载）
  secondme-dev-assistant/         # 开发者 skill（应用创建、OAuth、MCP、集成管理）
    SKILL.md                      # 概览和路由（< 500 行）
    references/                   # 详细参考文档（按需加载）
```

## Skills 编写规范

- SKILL.md 主体必须 < 500 行
- 详细内容放 references/ 目录（渐进式披露）
- Reference 引用只能一层深（SKILL.md → reference，不嵌套）
- 超过 100 行的 reference 文件必须有 TOC
- Skill name：仅小写字母 + 数字 + 连字符
- description 用第三人称，包含触发关键词
- SKILL.md frontmatter 应包含 license 字段（当前使用 MIT）

## Plugin Identity

- Plugin name: `secondme-skills`
- Skills: `secondme`, `secondme-dev-assistant`

## 域名规范

- **接口调用**（API、遥测上报等程序请求）一律用 `https://api.mindverse.com`，如 `{BASE} = https://api.mindverse.com/gate/lab`
- **安装源**：用户技能 `secondme` 唯一正式发布域名为 `https://second-me.cn`。所有面向用户的 CLI 安装命令使用 `npx skills add https://second-me.cn`，由根索引解析当前最新版，不固定技能或安装器版本。`/.well-known/agent-skills/index.json` 使用带 SHA-256 digest 的 v0.2 archive 格式并指向版本化发布包，旧版 `/.well-known/skills/index.json` 保留逐文件审计与兼容性，两个主索引都只含 `secondme`。默认不得带 `-y` 或 `-g`；只有用户明确确认全局范围时才添加 `-g`。开发者技能 `secondme-dev-assistant` 不进主索引，经 GitHub 安装：`npx skills add mindverse/second-me-skills -s secondme-dev-assistant -y -g`（GitHub 镜像需与 GitLab main 保持同步推送）
- `secondme` 技能不含任何遥测/数据上报逻辑（2026-07 移除）；`secondme-dev-assistant` 保留 opt-in 遥测
- **用户浏览器访问**统一 `*.second-me.cn` 域名家族：页面（登录/签约/协议/分享链接）`second-me.cn`，开发者控制台 `develop.second-me.cn`，文档站 `develop-docs.second-me.cn`，体验入口 `go.second-me.cn`，PRE 环境 `beta.second-me.cn`
- `second.me` 与 `app.mindos.com` 不出现在技能文档中（`second.me` 域名家族仍在线服务旧安装的更新，但文档一律只写 `second-me.cn`；解析用户给的历史分享链接按路径末段处理即可，与域名无关）
- `/contract/payment` 是协议文本页且必须带 `?tier=1|2|3`，不是收银台；实际付款在 App 账户页 / 分身分享页解锁流程
