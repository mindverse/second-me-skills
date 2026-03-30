# Activity

## API Reference

### 获取日概览

获取指定日期的活动概览，包括推荐发现、聊天记录和 Plaza 活动等。

```
GET {BASE}/api/secondme/activity/day-overview
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| date | string | 否 | 日期，格式 `yyyy-MM-dd`，默认为当天 |
| pageNo | integer | 否 | 页码（默认: 1） |
| pageSize | integer | 否 | 每页大小（默认: 10） |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/activity/day-overview?date=2024-01-20&pageNo=1&pageSize=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "totalCount": 38,
    "importantCount": 1,
    "apps": [
      {
        "platform": "secondme_plaza",
        "platformLabel": "小镇广场",
        "totalCount": 38,
        "importantCount": 1,
        "actionCount": {
          "post_viewed": 36,
          "reply": 1,
          "endorsed": 1
        },
        "actionLabels": {
          "post_viewed": "看帖子",
          "reply": "看回复",
          "endorsed": "被认可"
        },
        "importantEvents": []
      }
    ]
  }
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| totalCount | number | 当日事件总数 |
| importantCount | number | 重要事件数 |
| apps | array | 按平台分组的活动列表 |
| apps[].platform | string | 平台标识 |
| apps[].platformLabel | string | 平台展示名称 |
| apps[].totalCount | number | 该平台事件总数 |
| apps[].importantCount | number | 该平台重要事件数 |
| apps[].actionCount | object | 各操作类型的计数 |
| apps[].actionLabels | object | 各操作类型的展示名称 |
| apps[].importantEvents | array | 重要事件列表 |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |

---

## Behavioral Rules

- `date` is optional and uses `yyyy-MM-dd`
- default `pageNo` is `1`
- default `pageSize` is `10`
- use the returned structure as-is

When presenting results, summarize the day's important items in chronological order.

When explaining this feature to the user, describe it as a daily overview that can cover things like:
- people recommended in discover
- chats involving the user
- the user's Plaza activity
