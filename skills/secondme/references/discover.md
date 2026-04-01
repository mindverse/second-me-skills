# Discover

## API Reference

### 浏览推荐用户

获取推荐用户列表，支持基于地理位置的发现。此接口为发现式浏览，非自由文本语义搜索。

> **提示**: 此接口响应可能较慢，建议设置 60 秒超时。

```
GET {BASE}/api/secondme/discover/users
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| pageNo | integer | 否 | 页码（默认: 1） |
| pageSize | integer | 否 | 每页大小（默认: 20） |
| longitude | number | 否 | 经度，用于地理位置推荐 |
| latitude | number | 否 | 纬度，用于地理位置推荐 |
| circleType | string | 否 | 圈子类型筛选 |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/discover/users?pageNo=1&pageSize=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  --max-time 60
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "users": [
      {
        "userId": "12345",
        "username": "技术达人",
        "avatar": "https://cdn.example.com/avatar1.jpg",
        "route": "techguru",
        "distance": 5.2,
        "matchScore": 85,
        "title": "全栈工程师",
        "hook": "热爱开源，喜欢分享技术心得",
        "briefIntroduction": "10 年全栈开发经验，专注于 AI 和云计算领域",
        "friendStatus": "none",
        "commonFriends": [],
        "completionPercentage": 90
      }
    ],
    "searchRadius": 50,
    "totalCount": 100,
    "pageNo": 1,
    "pageSize": 20,
    "totalPages": 5,
    "hasMore": true
  }
}
```

#### 用户对象字段

| 字段 | 类型 | 说明 |
|------|------|------|
| userId | string | 用户 ID |
| username | string | 用户名 |
| avatar | string | 头像 URL |
| route | string | 用户主页路由 |
| distance | number | 距离 |
| matchScore | number | 匹配分数 |
| title | string | 标题 |
| hook | string | 引导语 |
| briefIntroduction | string | 简要介绍 |
| friendStatus | string | 好友状态 |
| commonFriends | array | 共同好友 |
| completionPercentage | number | 资料完成度 |

#### 顶层字段

| 字段 | 类型 | 说明 |
|------|------|------|
| users | array | 推荐用户列表 |
| totalCount | number | 总数 |
| pageNo | number | 当前页码 |
| pageSize | number | 每页大小 |
| hasMore | boolean | 是否有更多 |

#### 错误码

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |

---

## Usage Rules

`discover/users` may respond slowly. When calling it:

- If the caller supports a configurable timeout or wait window, set it to at least `60s` for this request
- Do not treat the request as failed before that wait window expires
- If the first attempt ends with a clear timeout or transient network timeout, retry once before surfacing failure
- If the caller has a hard timeout below `60s`, explain that the failure is likely caused by the runtime timeout rather than invalid discover parameters

This API supports discover-style browsing, not free-text semantic people search.

## Presentation Rules

When presenting recommended users:

- Always include a personal homepage link for each user
- Build that homepage as `https://second-me.cn/{route}`
- Do not show only the raw `route`
- If `route` is missing or blank, say clearly that the user's homepage is currently unavailable

If the user asks for highly specific semantic matching, explain that the current interface is discover-style browsing rather than free-text people search.

If the user asks to directly chat with those users, remind them that if they want to chat with people they are interested in, they can download SecondMe App, and output:

```
https://go.second-me.cn
```
