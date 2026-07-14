# 分身（Avatar）

本文件负责分身的创建、管理、定价、签约、评测和分发编排，并在末尾提供精简的 API 参考。普通创建讨论只需读取前面的流程与原则；需要调用接口、核对字段或解析响应时，再定位到 [API 参考](#api-参考)。

同一内核（Core）可创建多个分身。它们共享 Profile、记忆和内核，但各有独立的**分身定义**：这个最重要的字段决定身份、受众、价值、判断、表达、交互与边界；API 字段名为 `scenarioPrompt`。

## 目录

- [不可省略的规则](#不可省略的规则)
- [创建旅程](#创建旅程)
- [分身定义有效原则](#分身定义scenarioprompt有效原则)
- [收费与签约规则](#收费与签约规则)
- [标识符与上下文](#标识符与上下文)
- [API 参考](#api-参考)

## 不可省略的规则

- **只用用户资料**：默认来源仅限 Profile、Core、Note、Key Memory 和本次确认；外部资料须明确授权。
- **先查再问**：先读资料并起草，再补缺口；不重复询问已知信息。
- **逐轮补齐**：每轮最多问 1–2 个高影响问题，给默认建议和 2–3 个选项；禁止一次性索要完整 brief 或让用户从零写 prompt。
- **必要访谈**：创建前必须确认“服务谁”和“提供什么价值”，快速创建也不例外。
- **证据优先**：原文和具体事例优先；未验证推断不得写入分身定义。
- **官方技能 only**：只使用 `/avatar/skills/available` 返回的官方技能；不查询、展示、创建或绑定自定义技能。
- **不代办付款**：访客在分享页解锁付费分身；创作者在小己应用内充值回复额度。本技能只处理套餐配置和签约状态。
- **PAID 硬门**：保存 PAID 分身前必须重新查询签约状态，只有最新状态为 `SIGNED` 才能发送请求。
- **无转人工能力**：边界外只能说明范围、拒答，或引导到创作者真实提供的外部联系渠道；不得承诺系统会转接人工。
- **隐私与标识符隔离**：对外产物只出现 `shareCode`，不得暴露可枚举的 `avatarId`。

## 创建旅程

全新创建按以下顺序推进；用户明确点名某个阶段时直接跳转，但仍执行该阶段所需的安全检查。

```text
0 登录、Profile、首次查签约状态
→ 0.5 未签约时提前申请（可跳过）
→ 1 定义分身
→ 2 定向收集素材
→ 3 创建
→ 4 选择收费模式与套餐
→ 5 保存 PAID 前复查签约状态
→ 6 评测
→ 7 分发与运营
```

免费分身跳过 0.5 和 5。旅程中没有独立“付款”阶段。

### 阶段 0：登录、Profile 与首次签约查询

1. 按主 `SKILL.md` 完成鉴权并读取用户信息。
2. Profile 明显不完整且分身面向他人时，建议用户先补充，但不强制。
3. 创建意图一旦明确，立即查询 `/avatar/contract/status`；同时执行阶段 1 的信息扫描，不要等用户回答后再查。
4. 保留查询结果，供本次创建流程的后续阶段复用。

### 阶段 0.5：未签约时提前申请

根据首次查询结果处理：

| 状态 | 行为 |
|------|------|
| `SIGNED` | 静默跳过 |
| `PENDING` | 静默跳过，不重复给申请链接 |
| `NOT_SIGNED` | 只问一次是否提前申请，说明审核可与免费分身创建并行 |
| 查询失败 | 不推断状态，不阻塞 FREE 路径；PAID 保存前必须重查 |

用户愿意提前申请时，给出裸 URL：

```text
https://second-me.cn/contract/addendum
```

告诉用户提交后不用等待审核，可以先继续定义和创建分身。用户跳过、暂不确定或明确免费时继续旅程，不反复推销。

### 阶段 1：读取用户资料，完成必要访谈

在提问前读取用户自己的资料：

1. `/user/info`：`name`；`selfIntroduction`（技能内为 `about_me`）；`bio`（内核 Core，不是自我介绍）。
2. Note：先 `/note/list` 浏览，再用 `/note/search` 按方向找原文、案例、方法和表达。
3. Key Memory：先 `/memory/key/search` 扫描事实、风格和关系记忆，再按方向定向搜索。
4. 本次对话中用户明确说明或确认的信息。
5. `/avatar/list?pageNo=1&pageSize=100`：只查重，不作为用户信息来源。

默认不搜索互联网、公共人物资料或其他外部来源。只有用户明确授权时才搜索；外部内容须单独标注，并经用户确认后才能进入分身定义。

创建前必须确认：**服务谁**（目标用户、场景、问题或情绪）和**提供什么价值**（希望对方获得的判断、结果、行动或体验）。先依据已有资料给草案，不让用户从空白填写：

> 根据你现有的资料，我建议这个分身主要服务「{目标用户草案}」，帮助他们「{价值草案}」。这个方向符合你的预期吗？还是更接近 {备选方向}？

快速创建也不能跳过。其余信息按“典型问题 → 事实边界 → 交互姿态 → 语言指纹 → 名称和开场白”补齐，并标为“有依据 / 已确认 / 必须追问”；可选细节不阻塞创建。

语言指纹只能来自聊天、Note、自我介绍或语音转写；Core、职业和性格不能证明具体说法。证据不足时，让用户在两种说法中选择或提供一小段真实聊天；不得编造。

选一个主姿态，必要时再选一个次姿态：

| 姿态 | 核心行为 | 要防的塌陷 |
|------|----------|------------|
| `coach` 教练 | 通过追问帮助对方形成答案 | 被催促后直接替用户决定 |
| `companion` 陪伴 | 接住情绪，不急于解决 | 忍不住给方案和说教 |
| `advisor` 顾问 | 给明确判断和依据 | 含糊踢球或无事实硬断 |
| `thinker` 思想者 | 给非共识视角和深层解释 | 变成百科或鸡汤清单 |
| `expert` 专家 | 准确、直接地给结论 | 和稀泥、不敢做取舍 |
| `host` 主持 | 把话题聊开并推动对话 | 一本正经收成说教 |

把“塌陷”转成 1–2 个压力题，另准备 3–5 个典型问题供创建后检查。分身定义稳定后查询 `/avatar/skills/available?sceneMode=avatar_chat`，只推荐 0–3 个直接有价值的官方技能；用户确认后记录 `officialSkillKeys`。

创建字段中，`scenarioPrompt` 是按 Layer 0–3 生成的分身定义；`opening` 用“一句身份 + 一句能帮什么 + 一个引导问题”。`welcomeNote` 默认不发送：仅 PAID 分身确需在付费前展示可验证的背书、资历、成果或价值说明时，经用户确认后填写；FREE 和 SPONSORED 通常省略。其余可选字段为 `modes`、`distribution`、`monetization`、`material`、`relatedNoteIds` 和 `officialSkillKeys`。

调用创建接口前，以逐项短摘要确认定位、受众、价值、姿态、边界和关键假设；每轮最多确认 2–3 项。用户要求时再展示完整分身定义，不把全文审阅设为默认步骤。

### 阶段 2：按已确认方向深挖用户资料

受众和价值确认后，提取目标用户、问题、方法和语言关键词，定向搜索 Note 与 Key Memory。初始列表只建概览，不能替代定向搜索。

处理命中内容时：

- 身份、人格、世界观、判断方式、语言指纹和交互边界：提炼进分身定义的对应 Layer。
- 用户自己的方法论、框架、案例和隐喻：提炼进 Layer 3。
- 具体事件、数字、微故事、完整原话和长文：继续保留在 Note 或 Key Memory，必要时通过 `relatedNoteIds` / `material` 关联，不把分身定义写成资料库。
- 相互冲突或证据不足的内容：单独列为存疑项，请用户确认；不得自行选一条当事实。

只展示素材类别、少量关键例子和存疑项，不倾倒隐私原文或整批记忆。素材不足就缩短对应 Layer，不用通用内容撑长度。

### 阶段 3：创建分身

确保本次旅程已经做过首次签约状态查询；没有则先查。该检查不阻塞 FREE 创建。

- 没有启用官方技能：调用 `/avatar/create`。
- 启用了官方技能：调用 `/avatar/skill-create`，`skills` 中只传 `officialSkillKeys`。
- 创建时可直接带已确认的 `monetization`；PAID 必须先通过阶段 5 的最新签约检查。

成功后保留本次返回的 `avatarId` 和 `shareCode`，获取 `ownerRoute` 并输出完整分享链接。

### 阶段 4–5：收费模式、套餐与签约硬门

先让用户选择：

- `FREE`：访客免费聊，跳过签约硬门。
- `SPONSORED`：创作者用自己的回复额度为访客买单。
- `PAID`：访客付费解锁，至少配置一档套餐；保存前必须重新查签约状态。

PAID 参数确认完、用户明确要求保存后，紧接 create/update 前重新查询 `/avatar/contract/status`：

| 最新状态 | 保存行为 |
|----------|----------|
| `SIGNED` | 允许发送 PAID create/update |
| `PENDING` | 不发送；提示等待审核，可由用户选择先存 FREE |
| `NOT_SIGNED` | 不发送；给签约入口，可由用户选择先存 FREE |
| 查询失败 | 不发送；说明暂时无法核验，可由用户选择先存 FREE |

默认建议“先 FREE 创建、签约后 update 为 PAID”。保留已讨论好的套餐草稿；未经用户确认不得自动降级为 FREE。

具体 payload 和换算规则见 [收费与签约规则](#收费与签约规则)。

### 阶段 6：轻量评测

当前不提供自动模型仿真评分。用户要求测评时说明能力仍在建设，并完成两种人工验证：

1. **Owner 视角**：用聊天接口和本人的 `shareCode` 自测，检查知识、任务和场景人设。该视角可能认得主人、使用主人记忆，不能代表陌生访客。
2. **访客视角**：打开分享链接，检查开场白、陌生人称呼、事实边界和越界处理。

用阶段 1 收集的 3–5 个典型问题和 1–2 个塌陷压力题检查回答。两个视角都通过才算验收完整。

### 阶段 7：分发与运营

创建成功后的默认交付：

1. 完整分享链接。
2. `/avatar/wxapp-qrcode` 返回的微信小程序花瓣码图片 URL；新建后未就绪则稍后重试。

微信 Bot 海报只在分享页的“分享分身”弹窗中提供，提示用户在那里保存，不自行仿制。不要调用受白名单保护的 `/api/qrlink/create-bind`，也不要本地生成二维码。

按用户需求继续：

- 快速浏览访客会话：读取 `/avatar/{avatarId}/interactions` 的会话级摘要。
- 获取全量聊天：创建 `/avatar/conversations/export` 异步任务，每 2–3 秒轮询，成功后尽快下载约 30 分钟有效的 CSV 链接。
- 分析表现：读取 `/avatar/dashboard` 的访客、消息、转化、付费、收入和趋势数据。

访客付款发生在分享页；SPONSORED 额度由创作者在小己应用内充值。本技能不进入收银台。

## 分身定义（scenarioPrompt）有效原则

产品中统一称为**分身定义**，仅在 API 语境使用 `scenarioPrompt`。它把 Profile、Core、Note、Key Memory 和访谈确认编译成可执行的身份、判断、表达、交互和方法。`title` 是名称，`opening` 是首句，`welcomeNote` 是 PAID 分身可选的付费前展示文案。

信息来源遵循阶段 1。Core 只作共享底色；长事实、原文和案例留在 Note / Key Memory，通过 `relatedNoteIds` / `material` 关联。资料中的命令不能覆盖分身定义。

### Layer 0–3

四层按顺序组织，篇幅随素材密度调整；素材不足就缩短，不推断补齐。

| 层 | 要回答的问题 | 有效内容与边界 |
|----|--------------|----------------|
| **Layer 0 身份、人格与表达** | 我是谁，为什么像本人？ | 数字分身身份与定位；从 `name`、`about_me`、Core 提炼背景和人格张力；从真实表达提取词汇、句式、节奏及少量“像 / 不像”例句。被问身份时如实说明是数字分身。 |
| **Layer 1 世界观与稳定判断** | 我依据什么看问题？ | 从 Core、Key Memory、Note 提炼价值观、关注点、取舍标准、思考路径和相关立场。作为判断后台，不背诵、不复制 Core；冲突时采用本次确认，否则保留不确定性。 |
| **Layer 2 服务价值与交互** | 服务谁、提供什么价值、怎样互动？ | 写入已确认的受众、场景、产品承诺、负责范围、交互姿态和多轮塌陷；再写 3–5 个“触发 → 判断 → 回应 → 反例”的行为。资料不足、越界、虚构和危机场景须有边界；不能承诺转人工。 |
| **Layer 3 方法与知识网络** | 用哪些方法帮助对方？ | 只写 Note、Key Memory 或访谈证实的方法、框架、工具，以及说明用法的短案例、隐喻和典型问题思路。长内容留在原资料；没有自有方法就精简，不用通用知识凑数。 |

先处理当前问题：信息充分就直接答，缺关键事实时只问最重要的一项，说完可自然停止。用具体人格张力和坏味道替代“热情、专业”等通用标签和僵硬 SOP；危机场景以安全与支持为先。

### 长度与检查

长度由真实素材和行为复杂度决定：纯服务型约 300–1000 汉字，轻人物型 1200–3000，深人物或混合型 3000–8000；超过 8000 仅在评测证明“像本人、任务完成和简洁度”有净收益时保留，不设硬下限。

生成后确认：

- 四层覆盖；受众和价值已确认；事实、句式和案例可追溯。
- 没有编造、外部知识填空、Core 复制、资料堆积或其他字段重复。
- 回答符合本人判断、兑现承诺，没有通用 AI 腔和无必要展开。
- 只为评测暴露的真实问题加补丁；无净收益就回滚。

“你是一个热情专业的智能助手”不是分身定义：它没有本人、受众、价值、判断、表达、方法和边界。

## 收费与签约规则

### monetization payload

收费模式通过 create/update 的 `monetization` 对象设置：

FREE；编辑时显式发送，避免残留旧配置：

```json
{ "accessType": "FREE", "saleStatus": "ON_SALE", "currency": "CNY", "freeChatUnlimited": false }
```

SPONSORED；无价格套餐，由 owner 额度买单：

```json
{ "accessType": "SPONSORED", "accessScope": "PUBLIC", "saleStatus": "ON_SALE", "currency": "CNY" }
```

PAID 至少完整配置一档套餐：

| 套餐 | 价格字段 | 回复配额字段 |
|------|----------|--------------|
| 体验卡（3 天） | `threeDayPriceUnitAmount` | `threeDayReplyQuota` |
| 月卡（30 天） | `thirtyDayPriceUnitAmount` | `thirtyDayReplyQuota` |
| 年卡 | `yearPriceUnitAmount` | `yearReplyQuota` |

PAID 还可传 `freeChatCount`（0–10，默认建议 3）；保存时传 `agreementAccepted: true`，通常同时传 `accessType: PAID`、`saleStatus: ON_SALE`、`currency: CNY`。

### 价格换算与本地校验

`priceUnitAmount = 元 × 100,000`，不是“分”。例如：¥1 → `100000`，¥9.9 → `990000`，¥39 → `3900000`，¥99 → `9900000`。

请求前全部校验通过才发送：

1. 价格范围 ¥1–¥10,000，即 100,000–1,000,000,000 unit。
2. 默认回复配额为 `ceil(元 × 10)`；用户要求更高时，以该值为基准，若向上凑到整百只多不超过 10 轮，可采用整百上限，例如 ¥9.9 → 100、¥29 → 300、¥99 → 1000。
3. 回复配额必须为正整数；`freeChatCount` 必须为 0–10 的整数。
4. 至少一档套餐的价格和配额成对出现。

后端规则与本地校验不一致时，如实展示后端错误并以后端为准，不要反复用失败请求试错。

### 签约页面

签约申请页：

```text
https://second-me.cn/contract/addendum
```

付费服务协议文本页必须带 tier：

```text
https://second-me.cn/contract/payment?tier=1
```

`tier=1/2/3` 对应三档方案；不带 tier 会返回 404。该页面不是收银台。页面需要登录当前小己账号；向用户展示时使用裸 URL，不用 Markdown 包裹。

## 标识符与上下文

| | `avatarId` | `shareCode` |
|---|---|---|
| 性质 | 本人管理面内部整数主键，可枚举 | 公开随机句柄，不可枚举 |
| 用途 | detail、update、delete、set-default、interactions、dashboard、导出、花瓣码 | public、聊天、分享链接 |

转换方法：

- `shareCode → avatarId`：读取 `/avatar/public/{shareCode}` 的 `data.id`。
- `avatarId → shareCode`：读取 `/avatar/detail?avatarId=` 的 `data.shareCode`。
- 创建响应同时返回两者，本轮应同时保存，避免重复查询。

操作规则：

1. 用户给分享链接或 `shareCode`，做公开信息或聊天时直接用；做本人管理或数据操作时先转成 `avatarId` 并验证权限。
2. 用户给 `avatarId`，管理时直接用；生成分享物料或聊天时先转成 `shareCode`。
3. 他人分身通常只有公开入口；无法用他人的 `avatarId` 管理是正常权限设计。
4. 分享链接固定为 `https://second-me.cn/{ownerRoute}/avatar/{shareCode}`。缺少 `ownerRoute` 时读取 `/user/info` 的 `route`。
5. 列表展示每个分身的完整分享链接，不只展示 `shareCode`。

删除前必须展示目标并取得用户明确确认；`primary` 分身不可删除。

## API 参考

仅在需要调用具体接口、核对参数或解析响应时读取本节。

### 共同约定

- `{BASE}`、鉴权和凭据处理遵循主 `SKILL.md`；所有请求携带 `Authorization: Bearer <accessToken>`。
- 只调用 `{BASE}/api/secondme/avatar/...`，不要调用 Java 内部 `/rest/out/avatar/...` 或旧 App 内部接口。
- 写请求使用 `Content-Type: application/json`。
- 成功响应通常为 `{ "code": 0, "data": ... }`；非零 `code` 按原错误信息处理。
- `avatarId` 用于本人分身的管理操作；`shareCode` 用于公开信息、聊天和分享链接。转换规则见 [标识符与上下文](#标识符与上下文)。

### 端点索引

| 操作 | 方法与路径 | 标识符 |
|------|------------|--------|
| 列出本人分身 | `GET /avatar/list` | — |
| 获取本人分身详情 | `GET /avatar/detail` | `avatarId` |
| 查询签约状态 | `GET /avatar/contract/status` | — |
| 查询可用官方技能 | `GET /avatar/skills/available` | — |
| 创建带官方技能的分身 | `POST /avatar/skill-create` | — |
| 创建普通分身 | `POST /avatar/create` | — |
| 更新分身 | `POST /avatar/update` | `avatarId` |
| 删除分身 | `POST /avatar/delete` | `avatarId` |
| 设置默认分身 | `POST /avatar/{avatarId}/set-default` | `avatarId` |
| 获取公开信息 | `GET /avatar/public/{shareCode}` | `shareCode` |
| 获取交互摘要 | `GET /avatar/{avatarId}/interactions` | `avatarId` |
| 获取数据看板 | `GET /avatar/dashboard` | `avatarId` |
| 创建聊天记录导出任务 | `POST /avatar/conversations/export` | `avatarId` |
| 查询导出任务 | `GET /avatar/conversations/export/{jobId}` | `jobId` |
| 获取小程序花瓣码 | `GET /avatar/wxapp-qrcode` | `avatarId` |

以下路径均省略共同前缀 `{BASE}/api/secondme`。

### 查询与管理

#### 列出本人分身

```text
GET /avatar/list?pageNo=1&pageSize=20
```

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `pageNo` | integer | 否 | 默认 `1` |
| `pageSize` | integer | 否 | 默认 `20`，最大 `100` |

`data` 包含 `total` 和 `list`。列表项的常用字段：

- `avatarId`、`shareCode`、`title`
- `type`：`primary` 或 `custom`
- `scenarioPrompt`、`opening`
- `modes`、`distribution`
- `usageCount`、`viewCount`、`createdAt`

`primary` 是默认分身，不可删除；`custom` 可编辑和删除。

#### 获取本人分身详情

```text
GET /avatar/detail?avatarId={avatarId}
```

`avatarId` 为必需整数。`data` 返回完整分身配置及 `shareCode`，常用于编辑前读取当前值，或把 `avatarId` 转成 `shareCode`。

#### 更新分身

```text
POST /avatar/update
```

只发送需要修改的字段：

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `avatarId` | integer | 是 | 本人分身 ID |
| `title` | string | 否 | 分身名称 |
| `scenarioPrompt` | string | 否 | 分身定义 |
| `opening` | string | 否 | 开场白 |
| `welcomeNote` | string | 否 | PAID 分身可选的付费前展示文案；默认省略 |
| `modes` | object | 否 | 如 `textChat`、`voiceCall` |
| `distribution` | object | 否 | 如 `apiEnabled`、`wxappEnabled` |
| `monetization` | object | 否 | 收费配置，见前文规则 |
| `skillKeys` | string[] | 否 | 仅使用可用官方技能接口返回并经用户确认的 key |

成功时 `data` 返回更新后的分身。更新 PAID 配置前必须重新查询签约状态，且最新状态为 `SIGNED`。

#### 删除分身

```text
POST /avatar/delete
{ "avatarId": 3 }
```

只能删除 `custom` 分身。调用前必须向用户展示目标并取得明确确认。成功时 `data` 通常为 `null`。

#### 设置默认分身

```text
POST /avatar/{avatarId}/set-default
```

成功时 `data` 通常为 `null`。

### 创建与技能

#### 查询签约状态

```text
GET /avatar/contract/status
```

`data.status` 的可能值：

| 状态 | 含义 |
|------|------|
| `NOT_SIGNED` | 未提交签约申请 |
| `PENDING` | 已提交，审核中 |
| `SIGNED` | 已签约 |

接口失败时不要推断为已签约。FREE 创建可继续；PAID create/update 必须停在保存前。

#### 查询可用官方技能

```text
GET /avatar/skills/available?sceneMode=avatar_chat
```

`sceneMode` 可省略，默认 `avatar_chat`。`data.skills[]` 常用字段为：

- `skillKey`
- `displayName`
- `description`
- `enabled`

只推荐与当前分身直接相关的 0–3 个，并让用户确认。不要查询、展示或绑定自定义技能。

#### 创建普通分身

```text
POST /avatar/create
```

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 最长 100 字符 |
| `scenarioPrompt` | string | 否 | 分身定义 |
| `opening` | string | 否 | 访客进入时的第一条消息 |
| `welcomeNote` | string | 否 | PAID 分身可选的付费前展示文案；默认省略 |
| `modes` | object | 否 | `{ "textChat": bool, "voiceCall": bool }` |
| `distribution` | object | 否 | `{ "apiEnabled": bool, "wxappEnabled": bool }` |
| `monetization` | object | 否 | 收费配置，见前文规则 |

未启用官方技能时使用本接口。成功响应的关键字段是 `avatarId`、`shareCode`、`title` 和完整配置。

#### 创建带官方技能的分身

```text
POST /avatar/skill-create
```

在普通创建字段之外，可传：

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `material` | object | 否 | 分身材料 |
| `relatedNoteIds` | number[] | 否 | 分身专属召回资料 |
| `skills.officialSkillKeys` | string[] | 否 | 用户已确认的官方技能 key |

`skills` 当前只允许 `officialSkillKeys`。成功时关键结果位于 `data.avatar`，包括 `avatarId`、`shareCode` 和 `skillKeys`；`data.enabledSkillKeys` 表示实际启用项。

### 公开信息与运营数据

#### 获取公开信息

```text
GET /avatar/public/{shareCode}
```

`data` 常用字段：`id`、`shareCode`、`name`、`modes`、`interactionCount`、`viewCount`、`createdAt`、`ownerUserId`、`ownerRoute`、`ownerUsername`、`ownerAvatar`。

此接口可把 `shareCode` 转成 `avatarId`（`data.id`），但管理他人分身仍会被权限控制。

#### 获取交互摘要

```text
GET /avatar/{avatarId}/interactions
```

`data[]` 为会话级摘要，常用字段：`id`、`visitorName`、`messageCount`、`durationSeconds`、`summary`、`createdAt`。需要完整消息原文时使用异步导出，不要把摘要当作全量聊天记录。

#### 获取数据看板

```text
GET /avatar/dashboard?avatarId={avatarId}&from={ms}&to={ms}&interval=auto
```

| 参数 | 必需 | 说明 |
|------|------|------|
| `avatarId` | 是 | 本人分身 ID |
| `from` | 否 | 起始毫秒时间戳，默认 30 天前 |
| `to` | 否 | 结束毫秒时间戳，默认当前时间 |
| `interval` | 否 | 默认 `auto` |

`data.summary` 包含 `uniqueVisitorCount`、`messageUserCount`、`messageConversionRateBp`、`messageCount`、`paidUserCount`、`paidOrderCount`、`grossIncomeUnitAmount`；`data.trend[]` 返回按时间桶的访客、消息、订单和收入趋势。

- `messageConversionRateBp` 是万分比。
- `grossIncomeUnitAmount` 的单位与定价相同：元 × 100,000。

#### 导出完整聊天记录

创建任务：

```text
POST /avatar/conversations/export
{
  "avatarId": 15134,
  "appLanguage": "zh",
  "timezone": "Asia/Shanghai"
}
```

只有 `avatarId` 必需；响应返回 `data.jobId`。然后轮询：

```text
GET /avatar/conversations/export/{jobId}
```

直到 `data.status = SUCCEEDED`。成功结果包含 `downloadUrl`、`expiresAt`、`fileName`、`truncated`、`messageCount`。建议每 2–3 秒轮询；下载链接约 30 分钟失效，获取后尽快下载。

#### 获取小程序花瓣码

```text
GET /avatar/wxapp-qrcode?avatarId={avatarId}
```

成功时读取 `data.qrcodeUrl`。码图异步生成，新建分身返回空值或暂时报错时稍后重试。

### 常见错误

| 错误码 | 处理 |
|--------|------|
| `auth.token.invalid` | 清空会话上下文并重新登录 |
| `auth.scope.missing` | 告知缺少 `avatar.read` 或 `avatar.write` 权限 |
| `avatar.fetch.failed` | 告知读取失败，保留原上下文并按需重试 |
| `avatar.create.failed` | 展示后端错误，不假定已创建 |
| `avatar.update.failed` | 展示后端错误，不更新本地上下文 |
| `avatar.delete.failed` | 展示后端错误，不从上下文移除对象 |
| `avatar.contract.status_failed` | 不推断签约状态；FREE 可继续，PAID 保存暂停 |
