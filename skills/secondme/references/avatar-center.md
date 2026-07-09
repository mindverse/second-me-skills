# Avatar Studio（分身工场）

帮用户把 SecondMe 分身做成一个**可交付、可售卖、可分发的服务产品**。这不是一次性建完就走的表单，而是一条端到端旅程：产品定义 → 素材收集 → 建分身 → 定价收费 → 签约（付费必须）→ 评测 → 交付 HTML → 付费 → 分发。本文件同时收录分身 CRUD、API Key、交互记录等底层 API。

## Table of Contents

- [Avatar Studio 旅程](#avatar-studio-旅程)（先读这里）
- [新增能力细节](#新增能力细节)（scenarioPrompt 规范 / 定价 / 签约 / 交付 HTML / 付费 / 二维码 / 下载聊天记录）
- [API Reference](#api-reference)
  - [获取分身列表](#获取分身列表)
  - [获取分身详情](#获取分身详情)
  - [创建分身](#创建分身)
  - [更新分身](#更新分身)
  - [删除分身](#删除分身)
  - [设置默认分身](#设置默认分身)
  - [获取分身公开信息](#获取分身公开信息)
  - [获取交互记录](#获取交互记录)
  - [创建 API Key](#创建-api-key) / [列表](#获取-api-key-列表) / [更新](#更新-api-key) / [删除](#删除-api-key)
- [Share Link](#share-link)
- [Workflow Guidelines](#workflow-guidelines)

---

## Avatar Studio 旅程

这是本 skill 的核心。用户说「做一个分身」「创建分身」「把分身卖出去」「给分身定价」「分发分身」，或提到其中任一阶段时，进入本旅程。

**编排原则：**

- 全新创建时，按阶段顺序推进；用户直接点名某个阶段（如「帮我给分身定价」）时，跳到该阶段。
- 每个阶段结束后简短汇报产出，再进入下一步；不要一次把所有问题抛给用户。
- 付费相关阶段（签约、付费）是**浏览器流程**——像登录一样给用户一个 URL 让他在浏览器里完成，skill 不直接调接口。
- 免费分身（accessMode=FREE）跳过签约和付费两步。

**阶段总览：**

```
0 登录/资料 → 1 产品定义 → 2 收集素材 → 3 建分身 → 4 定价收费
   →〔5 签约〕→ 6 评测 → 7 交付HTML →〔8 付费〕→ 9 分发
                                          〔 〕= 付费分身专属
```

### 阶段 0 · 登录与资料前置

确保已登录（见 [connect.md](connect.md)）。若用户资料明显不完整、又要做面向他人的分身，建议先补资料（见 [profile.md](profile.md)），但不强制。

### 阶段 1 · 产品定义讨论

这是「更快做出好分身」的关键，替代直接让用户填字段。目标是回答清楚四件事：**对谁 × 提供什么 × 以什么身份口吻 × 到哪为止**。

按以下方法访谈（一次问一到两个问题，不要一次全抛）：

1. **一句话定位**：让用户用一句话描述「谁会来找这个分身、解决什么问题」。说不清时给参照选项（售后答疑 / 导购咨询 / 个人代表 / 知识咨询 / 培训问答…）。
2. **访客画像**：目标访客是谁（老客户 / 潜在客户 / 粉丝 / 同事…），他们带着什么问题、什么情绪来。
3. **典型问题清单**：和用户一起列出 **3–5 个分身必须答好的具体问题**。这份清单是写 scenarioPrompt 的骨架，也是将来评测的种子——务必落到具体问题，不接受「大概就是产品相关的」这类模糊回答。
4. **人设三件套**：身份（我是谁 / 代表谁 / 叫什么）、称呼（怎么称呼访客）、语气（亲切 / 专业 / 简洁…选 1–2 个词）。
5. **边界**：哪些问题不回答；什么情况转人工（要到转接话术和联系方式）；素材里没有的内容怎么兜底。
6. **压力演练**：从典型问题清单抽 1–2 个反问用户：「访客这么问，你希望分身怎么答？」用他的回答校准语气和详略。

访谈结束后，把结论转成草稿：

- `title`：分身名称
- `scenarioPrompt`：按 [scenarioPrompt 编写规范](#scenarioprompt-编写规范) 五段结构组装，逐条过一遍好 prompt 判定标准
- `opening`：开场白 = 一句身份 + 一句能帮什么 + 一个引导性问题
- `welcomeNote`：公开介绍文案

先把草稿完整念给用户确认（尤其 scenarioPrompt 全文），再进入下一步。

### 阶段 2 · 从记忆收集素材

用产品定义的关键词去用户已有的记忆里挖料，补全人设和知识：

- Key Memory 搜索：`GET {BASE}/api/secondme/memory/key/search`（见 [key-memory.md](key-memory.md)）
- 笔记列表 / 搜索：`POST {BASE}/api/secondme/note/list`、`/note/search`（见 [note.md](note.md)）

把命中的素材归纳进 `scenarioPrompt`，或作为 `relatedNoteIds` / `material` 关联给分身。向用户展示「我准备用这些素材」，确认后再建。

### 阶段 3 · 建分身

用阶段 1–2 的产出组装创建请求，一次成型，调用 [创建分身](#创建分身)：

```
POST {BASE}/api/secondme/avatar/create
```

传入 `title`、`scenarioPrompt`、`opening`、`welcomeNote`，以及可选的 `modes`、`distribution`、`monetization`（定价见阶段 4）。若需要同时新建并绑定自定义技能，后端另有 `POST {BASE}/api/secondme/avatar/skill-create`（本文件未展开其请求体，用前先确认字段）。

创建成功后拿到 `avatarId` 和 `shareCode`，拼出分享链接（见 [Share Link](#share-link)）念给用户。

### 阶段 4 · 定价与收费模式

分身有三种 access 模式，先问用户走哪种：

- **FREE 免费**：任何人免费聊，跳过签约和付费。
- **SPONSORED 我赞助**：创作者用自己的回复额度为访客买单（额度来自账户充值）。
- **PAID 向我订阅**：访客付费才能聊。需要先开通付费能力（阶段 5 签约）。

收费模式和套餐都通过 `monetization` 对象在 create/update 时传入：`accessType` 决定模式（`FREE` / `SPONSORED` / `PAID`）；PAID 需至少配置一档套餐（体验卡 / 月卡 / 年卡，各含价格和回复配额）。访谈式收集：先问模式，PAID 再逐档问定价。字段明细见 [定价与收费](#定价与收费monetization)。

### 阶段 5 · 签约（付费分身必须）

仅当用户选 PAID 且尚未开通付费能力时。这是浏览器流程，不是接口调用：引导用户打开签约页完成协议签署，开通后才能保存付费套餐。详见 [签约与付费（浏览器流程）](#签约与付费浏览器流程)。

### 阶段 6 · 评测（占位，后续深化）

分身建好后验证效果。**当前为轻量占位**：引导用户去 App / Web 亲自跟分身聊几句预览效果（见 [App Entry](#阶段-9--分发)），或人工检查开场白与几个典型问题的回答。

> 完整的「模型仿真测评 + 维度评分 + 优化建议」为后续版本能力，此处先不展开。用户明确要测评时，说明该能力正在建设中，先用人工预览兜底。

### 阶段 7 · 交付 HTML

为分身生成一个可交付的产品页（HTML），交给用户或其客户。页面由 skill 本地生成，取材：

- 分身公开信息：`GET {BASE}/api/secondme/avatar/public/{shareCode}`（标题、封面、开场白、介绍）
- 分享链接与二维码（见阶段 9）

页面内容建议包含：分身名称与介绍、服务说明（来自产品定义）、开场白示例、访问二维码、分享链接、（付费分身）套餐与价格。产出一个自包含 HTML 文件交付。

### 阶段 8 · 付费（付费分身开通 / 充值）

浏览器流程。两种场景：

- 创作者开通付费能力后的付款：打开 `/contract/payment` 页面完成。
- SPONSORED 模式需要更多回复额度：引导用户到账户页充值。

详见 [签约与付费（浏览器流程）](#签约与付费浏览器流程)。

### 阶段 9 · 分发

让分身触达访客：

- **二维码分发**：把分享链接生成二维码。skill 侧本地生成（后端 qrlink 短链接口有应用白名单限制，skill 不调用）。展示二维码 + 分享链接。
- **下载聊天记录**：导出分身的交互记录，`GET {BASE}/api/secondme/avatar/{avatarId}/interactions`。当前后端仅返回**会话级摘要**（访客名 / 消息数 / 时长 / summary），无逐字原文；导出时如实说明这一点。

分发完成后，可提示用户去 App / Web 查看分身实时表现或进一步分享：

```
https://go.second.me
```

---

## 新增能力细节

### scenarioPrompt 编写规范

scenarioPrompt 决定分身的行为质量，是整个旅程里最重要的产出。组装时按**五段结构**写，每段都不可缺：

| 段落 | 写什么 | 素材来源 |
|------|--------|----------|
| ① 身份与角色 | 我是谁、代表谁、叫什么名字 | 访谈 · 人设三件套 |
| ② 服务对象与任务 | 为谁服务；用**具体动词**描述核心任务（解答 / 推荐 / 收集 / 引导预约…）；覆盖典型问题清单 | 访谈 · 画像 + 问题清单 |
| ③ 知识与依据 | 回答依据什么素材；明确声明「素材里没有的不要编造」 | 阶段 2 收集的素材 |
| ④ 语气与表达 | 语气关键词；格式约束（如「先给结论，整体不超过三句」） | 访谈 · 人设 + 压力演练 |
| ⑤ 边界与兜底 | 不回答什么；何时用什么话术转人工；不确定时如何回应 | 访谈 · 边界 |

**好 prompt 的判定标准**——草稿写完逐条自检，不满足就改：

1. **具体可执行**：有明确的任务动词和对象。只有「热情」「专业」「回答各种问题」而没有具体任务的，是空话。
2. **单一聚焦**：一个分身只服务一个核心场景。用户想让分身「什么都能聊」时，建议拆成多个分身。
3. **有边界**：至少写明一类不处理的问题和对应的兜底动作。
4. **不编造**：知识依据和禁止编造声明必须在场。
5. **可测**：能从 prompt 直接反推出典型问题清单和期望的回答方式；反推不出来，说明第②段太虚。
6. **长度适中**：建议 150–500 字。太短必然空泛，太长稀释重点。

**反例**（不合格——五条标准全部违反）：

> 你是一个热情友好的智能助手，认真、专业地回答用户提出的各种问题，让用户感到满意。

**正例**（售后答疑场景，五段齐全，约 200 字）：

> 你是「元气茶饮」的售后客服分身，名叫小元。你服务的是已经下单或收到货的顾客，核心任务是：解答订单进度、处理常见饮品问题（口味异常、洒漏、错单）、指导优惠券使用。回答时依据店铺的售后规则素材，素材里没有的政策不要自行承诺。语气亲切、口语化，称呼顾客「亲」，先给处理结论再补充说明，整体不超过三句话。遇到退款、投诉或情绪激动的顾客，不要继续处理，回复「这个问题我帮您转给店长哦，您加微信 xxx」并结束该话题；拿不准的问题如实说「这个我需要确认一下」，不要编造答案。

### 定价与收费（monetization）

`monetization` 是 create/update 请求里的对象字段，透传给后端。**收费模式本身也在这个对象里设置**（`accessType`），不是独立参数。

通用键：

| 键 | 说明 |
|----|------|
| `accessType` | 收费模式：`FREE` / `SPONSORED` / `PAID` |
| `saleStatus` | 上架状态，通常传 `ON_SALE` |
| `currency` | 币种，中文环境传 `CNY` |

按模式的 payload 形态：

- **FREE**（编辑时显式下发，避免残留旧配置）：
  ```json
  { "accessType": "FREE", "saleStatus": "ON_SALE", "currency": "CNY", "freeChatUnlimited": false }
  ```
- **SPONSORED 我赞助**（无价格套餐，owner 额度买单）：
  ```json
  { "accessType": "SPONSORED", "accessScope": "PUBLIC", "saleStatus": "ON_SALE", "currency": "CNY" }
  ```
- **PAID 向我订阅**（至少配一档套餐，价格单位为最小货币单位「分」）：

  | 键 | 说明 |
  |----|------|
  | `threeDayPriceUnitAmount` / `threeDayReplyQuota` | 体验卡（3 天）价格 / 回复配额 |
  | `thirtyDayPriceUnitAmount` / `thirtyDayReplyQuota` | 月卡（30 天）价格 / 回复配额 |
  | `yearPriceUnitAmount` / `yearReplyQuota` | 年卡价格 / 回复配额 |
  | `freeChatCount` | 免费试聊次数（付费分身专属，非负整数） |
  | `agreementAccepted` | 保存付费套餐时传 `true` |

  校验规则：至少一档套餐完整（价格 + 配额成对）；价格有平台上下限；配额为正整数且受价格档位上限约束——被拒时把后端错误信息如实转告用户调整。

PAID 需先完成签约开通付费能力，否则保存付费套餐会被拒绝——此时转到签约流程。

### 签约与付费（浏览器流程）

签约和付费**不是 REST 接口**，而是在浏览器里完成的网页流程，模式同登录：给用户一个 URL，让其打开完成，不要用 markdown 链接语法包裹。

生产中文环境域名为 `second-me.cn`（PRE 为 `beta.second-me.cn`，与登录域名同源，按环境替换）：

- **签约（开通付费能力）**：
  ```
  https://second-me.cn/contract/addendum
  ```
  引导语示例：「做付费分身需要先签一份协议开通付费能力，点这个链接在浏览器里完成，完成后回来告诉我，我帮你配置套餐。」

- **付费**：
  ```
  https://second-me.cn/contract/payment
  ```

告知用户这些页面需要登录（withAuth），用当前 SecondMe 账号打开即可。完成后回到对话继续后续阶段。

### 交付 HTML 的取材

生成产品页时，先取分身公开信息 `GET {BASE}/api/secondme/avatar/public/{shareCode}`（无需鉴权），拿到标题、封面、开场白、介绍，结合产品定义访谈内容和分享链接/二维码，产出一个自包含 HTML 文件。

### 二维码分发

- 数据源：分享链接 `https://second-me.cn/{ownerRoute}/avatar/{shareCode}`。
- skill 侧本地把该链接编码成二维码图片（例如生成二维码并内嵌进交付 HTML，或产出独立图片文件）。
- 不调用后端 qrlink 接口：`/api/qrlink/create-bind` 受 `qrlink_bind_whitelist` 应用白名单保护且要求 OAuth2 app_id，普通用户 Auth Token 无权调用。

### 下载聊天记录

- 接口：`GET {BASE}/api/secondme/avatar/{avatarId}/interactions`（见 [获取交互记录](#获取交互记录)）。
- **限制**：当前仅返回会话级摘要（`visitorName` / `messageCount` / `durationSeconds` / `summary` / `createdAt`），**没有逐字对话原文**。导出时如实告知用户；完整逐字记录需后端后续暴露。
- 导出格式：按用户需要整理成 Markdown 或 CSV 交付。

---

## API Reference

### 获取分身列表

分页获取当前用户的所有分身。

```
GET {BASE}/api/secondme/avatar/list
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| pageNo | integer | 否 | 页码（默认: 1） |
| pageSize | integer | 否 | 每页大小（默认: 20，最大: 100） |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/avatar/list?pageNo=1&pageSize=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "total": 2,
    "list": [
      {
        "avatarId": 1,
        "type": "primary",
        "title": "My Avatar",
        "modes": { "textChat": true, "voiceCall": false },
        "distribution": { "apiEnabled": false, "wxappEnabled": false },
        "shareCode": "abc123",
        "usageCount": 10,
        "viewCount": 50,
        "createdAt": "2026-03-20 10:00:00"
      },
      {
        "avatarId": 2,
        "type": "custom",
        "title": "Sales Consultant",
        "scenarioPrompt": "你是一个专业的销售顾问...",
        "opening": "你好！有什么可以帮你的？",
        "modes": { "textChat": true, "voiceCall": true },
        "distribution": { "apiEnabled": true, "wxappEnabled": false },
        "shareCode": "def456",
        "usageCount": 5,
        "viewCount": 20,
        "createdAt": "2026-03-25 14:30:00"
      }
    ]
  }
}
```

#### 响应字段

| 字段 | 类型 | 说明 |
|------|------|------|
| total | number | 分身总数 |
| list[].avatarId | number | 分身 ID |
| list[].type | string | `primary`（默认分身，不可删除）或 `custom` |
| list[].title | string | 分身名称 |
| list[].scenarioPrompt | string | 场景提示词 |
| list[].opening | string | 开场白 |
| list[].modes | object | 交互模式配置 |
| list[].distribution | object | 分发渠道配置 |
| list[].shareCode | string | 分享码 |
| list[].usageCount | number | 已消耗配额 |
| list[].viewCount | number | 查看次数 |
| list[].createdAt | string | 创建时间 |

---

### 获取分身详情

获取指定分身的详细信息。

```
GET {BASE}/api/secondme/avatar/detail
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| avatarId | integer | 是 | 分身 ID |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/avatar/detail?avatarId=2" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "avatarId": 2,
    "type": "custom",
    "title": "Sales Consultant",
    "scenarioPrompt": "你是一个专业的销售顾问...",
    "opening": "你好！有什么可以帮你的？",
    "modes": { "textChat": true, "voiceCall": true },
    "distribution": { "apiEnabled": true, "wxappEnabled": false },
    "shareCode": "def456",
    "usageCount": 5,
    "viewCount": 20,
    "createdAt": "2026-03-25 14:30:00"
  }
}
```

---

### 创建分身

创建一个新的自定义分身。

```
POST {BASE}/api/secondme/avatar/create
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| title | string | 是 | 分身名称（最长 100 字符） |
| scenarioPrompt | string | 否 | 场景提示词（描述分身的任务和行为） |
| opening | string | 否 | 开场白（访客打开时的第一条消息） |
| welcomeNote | string | 否 | 公开介绍文案（展示在分身公开页） |
| modes | object | 否 | 交互模式：`{ "textChat": bool, "voiceCall": bool }` |
| distribution | object | 否 | 分发配置：`{ "apiEnabled": bool, "wxappEnabled": bool }` |
| monetization | object | 否 | 收费配置（见 [定价与收费](#定价与收费monetization)） |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/avatar/create" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "产品咨询助手",
    "scenarioPrompt": "你是一个专业的产品咨询顾问，负责回答客户关于产品功能和价格的问题。",
    "opening": "你好！我是产品咨询助手，请问有什么可以帮您的？",
    "modes": { "textChat": true, "voiceCall": false },
    "distribution": { "apiEnabled": true, "wxappEnabled": false }
  }'
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "avatarId": 3,
    "type": "custom",
    "title": "产品咨询助手",
    "scenarioPrompt": "你是一个专业的产品咨询顾问...",
    "opening": "你好！我是产品咨询助手...",
    "modes": { "textChat": true, "voiceCall": false },
    "distribution": { "apiEnabled": true, "wxappEnabled": false },
    "shareCode": "ghi789",
    "usageCount": 0,
    "viewCount": 0
  }
}
```

---

### 更新分身

更新指定分身的配置。仅传入需要修改的字段。

```
POST {BASE}/api/secondme/avatar/update
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| avatarId | integer | 是 | 分身 ID |
| title | string | 否 | 分身名称 |
| scenarioPrompt | string | 否 | 场景提示词 |
| opening | string | 否 | 开场白 |
| welcomeNote | string | 否 | 公开介绍文案 |
| modes | object | 否 | 交互模式配置 |
| distribution | object | 否 | 分发渠道配置 |
| monetization | object | 否 | 收费配置（见 [定价与收费](#定价与收费monetization)） |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/avatar/update" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "avatarId": 3,
    "title": "产品咨询助手 v2",
    "opening": "欢迎！我是升级后的产品顾问，请问有什么可以帮您？"
  }'
```

#### 响应

**成功 (200)**: 返回更新后的完整分身数据（结构同创建响应）。

---

### 删除分身

删除指定的自定义分身。**primary 类型的分身不可删除。**

```
POST {BASE}/api/secondme/avatar/delete
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| avatarId | integer | 是 | 分身 ID |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/avatar/delete" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "avatarId": 3 }'
```

#### 响应

**成功 (200)**

```json
{ "code": 0, "data": null }
```

---

### 设置默认分身

将指定分身设为默认分身。

```
POST {BASE}/api/secondme/avatar/{avatarId}/set-default
```

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| avatarId | integer | 是 | 分身 ID |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/avatar/2/set-default" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{ "code": 0, "data": null }
```

---

### 获取分身公开信息

通过 shareCode 获取分身的公开信息（包含 owner 信息）。

```
GET {BASE}/api/secondme/avatar/public/{shareCode}
```

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| shareCode | string | 是 | 分身分享码 |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/avatar/public/abc123" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "id": 1,
    "shareCode": "abc123",
    "name": "My Avatar",
    "modes": { "textChat": true, "voiceCall": false },
    "interactionCount": 10,
    "viewCount": 50,
    "createdAt": "2026-03-20 10:00:00",
    "ownerUserId": 12345,
    "ownerRoute": "john",
    "ownerUsername": "John",
    "ownerAvatar": "https://..."
  }
}
```

---

### 获取交互记录

获取指定分身的访客交互历史。

```
GET {BASE}/api/secondme/avatar/{avatarId}/interactions
```

#### 路径参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| avatarId | integer | 是 | 分身 ID |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/avatar/2/interactions" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": [
    {
      "id": 1,
      "visitorName": "访客A",
      "messageCount": 15,
      "durationSeconds": 300,
      "summary": "客户咨询了产品价格和功能...",
      "createdAt": "2026-03-28 09:00:00"
    }
  ]
}
```

---

### 创建 API Key

为指定分身创建 API Key。用于开放 API 分发，允许第三方通过 API Key 与分身对话。

```
POST {BASE}/api/secondme/avatar/api-key/create
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| avatarId | integer | 是 | 分身 ID |
| name | string | 是 | 密钥备注名（最长 100 字符） |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/avatar/api-key/create" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "avatarId": 2, "name": "接入官网" }'
```

#### 响应

**成功 (200)**

```json
{
  "code": 0,
  "data": {
    "keyId": 1,
    "avatarId": 2,
    "name": "接入官网",
    "secretKey": "sk-e5443b6842d54208bc2c9a0bc2b65376",
    "enabled": true
  }
}
```

> **Important**: `secretKey` 仅在创建时返回明文，之后不再展示。请提醒用户妥善保存。

---

### 获取 API Key 列表

获取指定分身的所有 API Key。

```
GET {BASE}/api/secondme/avatar/api-key/list
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| avatarId | integer | 是 | 分身 ID |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/avatar/api-key/list?avatarId=2" \
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
        "keyId": 1,
        "avatarId": 2,
        "name": "接入官网",
        "enabled": true
      }
    ]
  }
}
```

---

### 更新 API Key

更新 API Key 的名称或启停状态。

```
POST {BASE}/api/secondme/avatar/api-key/update
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| keyId | integer | 是 | 密钥 ID |
| name | string | 否 | 新的备注名 |
| enabled | boolean | 否 | 是否启用 |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/avatar/api-key/update" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "keyId": 1, "enabled": false }'
```

#### 响应

**成功 (200)**

```json
{ "code": 0, "data": null }
```

---

### 删除 API Key

永久删除指定的 API Key。

```
POST {BASE}/api/secondme/avatar/api-key/delete
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| keyId | integer | 是 | 密钥 ID |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/avatar/api-key/delete" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "keyId": 1 }'
```

#### 响应

**成功 (200)**

```json
{ "code": 0, "data": null }
```

---

## Error Codes

| 错误码 | 说明 |
|-------|------|
| auth.token.invalid | Token 无效或已过期 |
| auth.scope.missing | 缺少必需的权限（需要 avatar.read 或 avatar.write） |
| avatar.fetch.failed | 获取分身信息失败 |
| avatar.create.failed | 创建分身失败 |
| avatar.update.failed | 更新分身失败 |
| avatar.delete.failed | 删除分身失败 |
| avatar.apikey.failed | API Key 操作失败 |

---

## Share Link

分身的分享链接格式：

```
https://second-me.cn/{ownerRoute}/avatar/{shareCode}
```

- `ownerRoute`: 用户的主页路由（从 `GET {BASE}/api/secondme/user/info` 响应的 `route` 字段获取）
- `shareCode`: 分身的分享码（从创建/详情接口返回）

在展示分身信息时，始终拼接并展示完整的分享链接，而不是只展示 shareCode。

---

## Workflow Guidelines

### 创建分身

全新创建分身时，走 [Avatar Studio 旅程](#avatar-studio-旅程)（产品定义 → 收集素材 → 建分身 …），不要直接让用户裸填字段。用户只想快速建一个最小分身时，至少确认 `title`（必填）、`scenarioPrompt`（建议）、`opening`（可选）。

创建成功后，拼接完整分享链接 `https://second-me.cn/{ownerRoute}/avatar/{shareCode}` 并展示给用户。如果当前上下文中没有用户的 `route`，先调用 `GET {BASE}/api/secondme/user/info` 获取。

### 列表展示

- `type: "primary"` 是默认分身（每用户一个，不可删除），在列表中标注
- `type: "custom"` 是自定义分身，可以编辑和删除
- 每个分身都应展示完整分享链接 `https://second-me.cn/{ownerRoute}/avatar/{shareCode}`

### API Key 管理

- 创建后 **立即** 展示 `secretKey` 并提醒用户保存（仅展示一次）
- 发现用量异常时可以 disable 单个 Key，不影响其他 Key
- 删除 API Key 前需要用户确认

### 删除确认

删除分身或 API Key 前，展示即将删除的对象信息并要求用户明确确认。
