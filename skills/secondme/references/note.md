# Note

## API Reference

### 添加笔记

新建一条笔记，支持文本（TEXT）和链接（LINK）两种类型。

```
POST {BASE}/api/secondme/note/add
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| content | string | TEXT 必填 | 笔记内容（最长 50000 字符） |
| title | string | 否 | 笔记标题（最长 200 字符） |
| urls | array[string] | LINK 必填 | URL 列表（最多 10 条），后端会自动提取内容 |
| memoryType | string | 否 | 笔记类型：`TEXT`（默认）或 `LINK` |

#### 请求示例

**文本笔记**

```bash
curl -X POST "{BASE}/api/secondme/note/add" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "memoryType": "TEXT",
    "content": "周末读完的《三体》笔记：黑暗森林法则……",
    "title": "三体读书笔记"
  }'
```

**链接笔记**

```bash
curl -X POST "{BASE}/api/secondme/note/add" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "memoryType": "LINK",
    "urls": ["https://example.com/article"],
    "title": "值得精读的文章"
  }'
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "noteId": 98765
  }
}
```

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| note.add.not_whitelisted | 当前应用未被授权调用添加接口 |

---

### 搜索笔记

按关键词搜索笔记，支持分页。

```
GET {BASE}/api/secondme/note/search
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词（默认空） |
| pageNo | integer | 否 | 页码（默认 1） |
| pageSize | integer | 否 | 每页数量（默认 20，最大 100） |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/note/search?keyword=三体&pageNo=1&pageSize=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": 98765,
        "title": "三体读书笔记",
        "content": "黑暗森林法则……",
        "memoryType": "TEXT",
        "createTime": 1705315800000,
        "updateTime": 1705315800000
      }
    ],
    "total": 1
  }
}
```

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |

---

### 列出笔记

读取当前用户的笔记列表（含原始内容与附件），**支持按分类（dataTypes）单选或组合过滤**，也支持关键词过滤。不传 `dataTypes` 时返回全部类型。

```
POST {BASE}/api/secondme/note/list
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| from | integer | 否 | 分页起始位置（默认 0） |
| size | integer | 否 | 每页数量（默认 20，最大 100） |
| dataTypes | array[string] | 否 | 数据类型过滤。可选值：`Doc`, `Audio`, `Link&Doc`, `Answer`, `Image`, `Memo`, `Link`, `Chat`, `Chat&Answer` |
| query | string | 否 | 搜索关键词（最长 200） |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/note/list" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "from": 0,
    "size": 20,
    "dataTypes": ["Memo", "Link"],
    "query": "三体"
  }'
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "list": [
      {
        "id": 98765,
        "type": "note",
        "sortTimestamp": 1705315800000,
        "note": {
          "title": "三体读书笔记",
          "content": "黑暗森林法则……",
          "memoryType": "TEXT",
          "attachments": [
            {
              "url": "https://cdn.example.com/cover.jpg",
              "dataType": "Image"
            }
          ]
        }
      }
    ],
    "total": 1
  }
}
```

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| note.list.not_whitelisted | 当前应用未被授权调用列表接口 |

---

### 更新笔记

更新指定笔记的内容或标题。仅传需要修改的字段；笔记类型（memoryType）创建后不可变。

```
POST {BASE}/api/secondme/note/{note_id}/update
```

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| note_id | number | 是 | 笔记 ID |

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| content | string | 否 | 更新后的笔记内容（最长 50000） |
| title | string | 否 | 更新后的笔记标题（最长 200） |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/note/98765/update" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "黑暗森林法则：宇宙是一座黑暗森林……（补充）",
    "title": "三体读书笔记 v2"
  }'
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": null
}
```

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| note.update.failed | 更新笔记失败 |

---

### 删除笔记

删除指定的笔记。

```
POST {BASE}/api/secondme/note/{note_id}/delete
```

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| note_id | number | 是 | 笔记 ID |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/note/98765/delete" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": null
}
```

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| note.delete.failed | 删除笔记失败 |

---

## Contents

- [Overview](#overview)
- [Add Note](#add-note)
- [Search Note](#search-note)
- [List Note](#list-note)
- [Update Note](#update-note)
- [Delete Note](#delete-note)

## Overview

Note 用来保存用户的片段记录：读书笔记、灵感、链接收藏、会话摘录等。

- **Note vs Key Memory**：Note 是可读可编辑的内容片段（类似便签/收藏夹），有 TEXT 与 LINK 两种类型；Key Memory 是用于塑造 SecondMe 的结构化长期事实。两者不要混用。
- **两类查询接口**：`search` 只返回标题和内容片段，适合关键词命中；`list` 返回完整对象（含附件 `attachments`），适合浏览或展示。

## Add Note

Rules:

- 若用户给出一段文字要收藏，默认使用 `memoryType=TEXT`，将正文放入 `content`
- 若用户给出一个或多个链接想收藏，使用 `memoryType=LINK` 并把 URL 放入 `urls`（最多 10 条）
- `title` 可选，但建议替用户生成或摘取一个简短标题，便于后续检索
- 创建成功后复述返回的 `noteId`，便于后续更新或删除时引用
- **Auto-import hint**：本会话内**首次** add 成功后，用一句话顺嘴提示用户"也可以配个定时任务自动调用这个接口同步内容"——只是告知有这个选项，**不要**列方案、贴 cron 示例、追问"是否需要我帮你配置"。同会话后续 add 不再重复这句提示，search / list / update / delete 也不要带。如果用户主动接话或问起怎么搞，再根据其平台/环境（Mac launchd、Linux cron、服务器、Claude Code `/schedule` 等）讨论具体做法

## Search Note

Rules:

- 有明确关键词、想在已有笔记里查找时使用 `search`
- `pageSize` 默认 20 就够；若用户只想看前几条，缩到 5–10 即可
- 命中为空时不要反复改写 query，先如实告知用户并询问是否调整关键词

## List Note

Rules:

- 想浏览完整笔记（含附件、图片、音频等）时使用 `list`
- **按分类过滤**：在 `dataTypes` 中传入需要的分类，只返回这些分类的笔记
  - 只看备忘 → `["Memo"]`
  - 只看链接收藏 → `["Link"]`
  - 同时看备忘和链接 → `["Memo", "Link"]`
  - 看聊天衍生内容 → `["Chat", "Chat&Answer"]`
  - 看图片/音频 → `["Image"]` / `["Audio"]`
- 不传 `dataTypes` 时按时间倒序返回全部类型
- 关键词过滤用 `query`；可以和 `dataTypes` 组合使用

## Update Note

Rules:

- 更新前和用户确认目标笔记（通过 `noteId` 或先 `search` 找到）
- 只发送需要变更的字段；未修改的字段不要重传
- 笔记类型（TEXT / LINK）创建后不可变；如果用户想改类型，请新建一条并删除旧的

## Delete Note

Rules:

- 删除前向用户确认要删除的笔记（通过 `noteId` 核对标题和内容片段）
- 成功删除后简要告知"已删除 noteId=xxx"，避免静默操作
- 批量删除时逐条请求并汇总结果，避免一次失败导致状态不明
