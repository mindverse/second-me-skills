# 关键记忆（Key Memory）

## API Reference

### 插入关键记忆

直接写入一条经用户确认的关键事实。此接口没有记忆类型参数，不得伪造或猜测类型字段。

```
POST {BASE}/api/secondme/memory/key
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| content | string | 是 | 记忆内容（最长 5000 字符） |
| visibility | int | 否 | 可见性，`1` 为可见（默认: 1） |
| mode | string | 否 | 固定值 `direct`（默认: "direct"） |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/memory/key" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "direct",
    "content": "喜欢在周末阅读科幻小说",
    "visibility": 1
  }'
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {}
}
```

返回空对象表示创建成功。

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| memory.content.required | 缺少 content 字段 |

---

### 搜索关键记忆

按关键词搜索关键记忆，支持分页。

```
GET {BASE}/api/secondme/memory/key/search
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| keyword | string | 否 | 搜索关键词 |
| pageNo | integer | 否 | 页码（默认: 1） |
| pageSize | integer | 否 | 每页大小（默认: 20） |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/memory/key/search?keyword=阅读&pageNo=1&pageSize=20" \
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
        "id": 12345,
        "factActor": "用户",
        "factObject": "兴趣爱好",
        "factContent": "喜欢在周末阅读科幻小说",
        "createTime": 1705315800000,
        "updateTime": 1705315800000,
        "visibility": 1
      }
    ],
    "total": 1
  }
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| list | array | 关键记忆列表 |
| list[].id | number | 记忆 ID |
| list[].factActor | string | 事实主体 |
| list[].factObject | string | 事实对象/分类 |
| list[].factContent | string | 事实内容 |
| list[].createTime | number | 创建时间（毫秒时间戳） |
| list[].updateTime | number | 更新时间（毫秒时间戳） |
| list[].visibility | number | 可见性 |
| list[].userId | number | 用户 ID |
| list[].dataType | string | 数据类型 |
| list[].memoryKind | string | 关键记忆类型（以接口返回值为准） |
| list[].readStatus | string | 已读状态 |
| list[].memoryState | string | 记忆状态 |
| total | number | 总数 |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |

---

### 更新关键记忆

更新指定的关键记忆内容。

```
POST {BASE}/api/secondme/memory/key/{memory_id}/update
```

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| memory_id | number | 是 | 关键记忆 ID |

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| content | string | 否 | 更新后的记忆内容 |
| visibility | number | 否 | 可见性，`1` 为可见 |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/memory/key/12345/update" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "喜欢在周末阅读科幻小说和技术书籍",
    "visibility": 1
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
| memory.not_found | 指定的关键记忆不存在 |

---

### 删除关键记忆

删除指定的关键记忆。

```
POST {BASE}/api/secondme/memory/key/{memory_id}/delete
```

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| memory_id | number | 是 | 关键记忆 ID |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/memory/key/12345/delete" \
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
| memory.not_found | 指定的关键记忆不存在 |

---

## 目录

- [概念说明](#概念说明)
- [引导同步事实型关键记忆](#引导同步事实型关键记忆)
- [插入事实型关键记忆](#插入事实型关键记忆)
- [批量创建事实型关键记忆](#批量创建事实型关键记忆)
- [搜索关键记忆操作规则](#搜索关键记忆操作规则)
- [更新关键记忆操作规则](#更新关键记忆操作规则)
- [删除关键记忆操作规则](#删除关键记忆操作规则)

## 概念说明

关键记忆是小己记忆系统的结构化理解层，分为三类：

1. **事实型关键记忆**：记录用户的关键事实，如偏好、经历、习惯等，让分身更懂真实的用户。用户（主人）与分身对话时，系统会自动生成此类记忆。
2. **风格型关键记忆**：记录用户的表达习惯和话题禁忌，让分身知道什么该说、什么不该说、怎么说。
3. **关系型关键记忆**：记录用户与他人的关系和相处方式，让分身理解他们在用户生活中的角色。分身与他人对话时，系统会自动生成此类记忆。

搜索结果中如果有 `memoryKind`，按接口实际返回值展示类型；不得自行发明枚举值。当前直接写入接口不接受类型字段，只用于写入用户确认的关键事实；不得声称可以手动指定风格型或关系型。

如果用户只笼统地说「记忆」、`memory`、「你记得吗」或「查我的记忆」，不要默认就是指关键记忆；用户也可能在说当前智能体的本地记忆，或小己的资料。

如果上下文无法判断，询问：

> 你想查当前智能体的本地记忆，还是小己里的资料或关键记忆？

## 引导同步事实型关键记忆

If the user is in onboarding, or asks how to shape their 小己（Second Me） avatar faster, offer:

> 如果你愿意，我可以把适合长期保存的关键事实整理成几条，再分条存进小己（Second Me）。
>
> 这样通常能更快塑造你的小己分身。
>
> 要我先整理一版给你确认吗？

Rules:

- ask for consent before preparing or writing a sync batch
- if the user accepts from the first-login handoff, first review local memory and extract candidate facts that are suitable for long-term storage in 小己（Second Me）
- if there are no suitable local memory facts, say so clearly and do not push the import step
- if the user agrees, first show the candidate facts in a compact list
- only write the facts the user confirms
- prefer durable facts such as preferences, stable background, and long-term context
- for this onboarding sync flow, use the batch create endpoint below after the user confirms the list
- after batch create succeeds, report the returned `insertedCount`

## 插入事实型关键记忆

直接写入只用于经用户确认、适合长期保留的关键事实，例如：

- 用户偏好
- 稳定的个人经历
- 长期习惯与背景事实

关系型关键记忆由分身与他人的对话自动生成，不要把普通的人际关系描述冒充为可手动指定类型的关系型记忆。

## 批量创建事实型关键记忆

Use batch create when the user confirms multiple memory items at once.

There is no dedicated batch endpoint. To insert multiple memories, call the single insert endpoint once per item. Send one request per memory item sequentially. After all requests complete, report how many were inserted successfully.

## 搜索关键记忆操作规则

Do not merge local memory results with 小己（Second Me） Key Memory results unless the user explicitly asks for both.

## 更新关键记忆操作规则

Rules:

- update only after the user confirms which memory to change
- only send the fields the user wants changed

## 删除关键记忆操作规则

Rules:

- confirm the deletion target with the user before calling delete
