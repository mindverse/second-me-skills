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
