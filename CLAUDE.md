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

- **接口调用**（API、遥测上报等程序请求）一律用 `https://api.mindverse.com`，如 `{BASE} = https://api.mindverse.com/gate/lab`，不随安装来源切换
- **安装源**：规范入口 `https://second.me`（well-known 分发）；`https://second-me.cn` 是内容字节一致的大陆镜像入口，可作为安装源。安装指引里只出现这两个域名
- **用户浏览器访问**按安装来源自适应 `{DOMAIN}` 域名家族（`second.me` 或 `second-me.cn`；pre-flight 从 `~/.agents/.skill-lock.json` 的安装来源解析出 `SM_DOMAIN`，`~/.secondme/config` 的 `domain` 字段可覆盖）：登录/签约/协议/分享链接 `{DOMAIN}`，开发者控制台 `develop.{DOMAIN}`，体验入口 `go.{DOMAIN}`；解析用户提供的分享链接时两个域名都接受
- 文档站抓取固定 `develop-docs.second.me`，不随入口切换；PRE 环境 `beta.second.me`
- `app.mindos.com` 不出现在技能文档中（部分国内网络 TLS 握手失败，2026-07 实测）
- `/contract/payment` 是协议文本页且必须带 `?tier=1|2|3`，不是收银台；实际付款在 App 账户页 / 分身分享页解锁流程
