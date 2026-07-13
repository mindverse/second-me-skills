# 分身中心改造设计：从全功能入口到分身工场

- 日期：2026-07-08（2026-07-09 修订：范围从「四段质量闭环」扩为完整商业化链路）
- 状态：流程已铺全景，签约状态查询已补齐
- 范围：second-me-skills（skill 侧） + secondme 后端 `biz/labs_apps_backend`（服务侧）
- 版本影响：`secondme` skill 2.3.2 → 3.0.0（破坏性收窄）

## 0. 背景与目标

现有 `secondme` skill 覆盖登录、社交、记忆、技能市场等十余个模块，其中 Plaza、好友、发现、动态、第三方技能后续不再需要。改造后 skill 收窄为「个人账户 + 分身工场」：保留基础模块，把重心放到帮用户**把 SecondMe 分身做成一个可交付、可售卖、可分发的服务产品**。

这不是一个「创建 + 调优」的小闭环，而是一条端到端的商业化链路。测评只是其中一个节点，不是中心。

## 0.1 端到端流程（含后端能力盘点）

按逻辑顺序排列（用户原始清单为头脑风暴顺序，此处为建议执行序）；每步标注后端支撑现状：

| # | 步骤 | 后端支撑 | 依据 / 端点 |
|---|------|----------|-------------|
| 1 | 已有信息扫描 | ✅ 有 | Agent 当前稳定上下文 / 本地 memory（若可用）+ `/user/info` + `/user/shades` + Key Memory + notes list + avatar list；本地 memory 未确认不上传 |
| 2 | 渐进式产品定义（面向谁、提供什么服务） | ✅ skill 编排 | 先用已有信息拟草案，每轮只追问 1–2 个高影响缺口，禁止一次性 brief |
| 3 | 按已确定方向深挖素材 | ✅ 有 | `/api/secondme/memory/key/search` + notes list/search；人格与行为进 prompt，具体事实和长文留在记忆 / Notes |
| 4 | 建分身 | ✅ 有 | `/api/secondme/avatar/create`、`/avatar/skill-create` |
| 5 | 定价与收费模式 | ✅ 有（字段） | avatar `monetization`（halfHourReplyQuota / yearReplyQuota / freeChatCount / freeChatUnlimited），无独立定价接口 |
| 6 | 签合同（付费分身必须） | ✅ 有 | 浏览器签约页 `/contract/addendum` + Labs 状态查询 `GET /api/secondme/avatar/contract/status` |
| 7 | 评测 | 🆕 待建（先占位） | 新增 evaluation 模块，深化留后期（见 §4） |
| 8 | 交付 HTML | ⚠️ 部分 | 公开页 `/api/secondme/avatar/public/{shareCode}` 有；HTML 生成为 skill 侧产出 |
| 9 | 付费 | ❌ **缺口** | 收款在 os-main + bill-center；labs 仅有 `create_external_avatar_unlock_state`（访客解锁） |
| 10a | 二维码分发 | ✅ 有 | `qrlink` 模块：`/api/qrlink/create-bind`、`/api/admin/qrlink/{slug}/image.png` |
| 10b | 下载聊天记录 | ⚠️ 只能导摘要 | `get_avatar_interactions` 仅返回会话级摘要（访客名 / 条数 / 时长 / summary），无对话原文 |

图示：

```
profile → 产品定义 → 收集素材 → 建分身 → 定价 →〔签合同*〕→ 评测 → 交付HTML →〔付费*〕→ 分发(二维码 + 聊天记录)
                                                  * 付费分身路径专属
```

## 0.2 原始三处缺口（持续收口）

1. **签合同**：已收口。申请在 `/contract/addendum` 浏览器页面完成；Skill 通过 `GET /api/secondme/avatar/contract/status` 读取 `NOT_SIGNED` / `PENDING` / `SIGNED` 归一化状态，不接触合同正文或敏感信息。
2. **付费语义**：这步是谁付钱？(A) 创作者付费开通付费分身（平台侧收费）；(B) 配置「访客付费解锁聊天」（对应 `unlock_state`）。两者流程完全不同。
3. **下载完整聊天记录**：现状只能导会话摘要。完整原文需推 os-main 暴露 transcript（与评测同一依赖）。先接受「只导摘要」，还是列为对 os-main 的硬需求。

评测节点的实现细节（复用 visitor_chat 的凭证 / WS / 配额问题）见 §4 与 §8，本期先占位、按用户要求后期深化。

## 1. 决策记录

| 议题 | 决策 |
|------|------|
| 删除边界 | plaza / friend / discover / activity / third-party-skills 五个模块，连带邀请码准入、App 下载提醒策略全删；connect / profile / chat / key-memory / note 保留不动 |
| 测评方式 | 后端新增测评能力：模型生成仿真对话，真实跑分身链路，对照预期评分 |
| 改造范围 | 前后端一起设计实现（second-me-skills + labs_apps_backend） |
| 引导创建 | 访谈式引导：逐步提问后组装创建参数 |
| 优化闭环 | 测评报告直接产出优化建议，skill 展示 diff，用户确认后调 update 修改 prompt，随后提示再次测评对比 |
| 交互洞察 | 本期不做独立洞察模块；真实交互数据接入测评列为后续演进 |
| 代码检出 | 后端新 clone 到 `workspace/secondme-cccc`，从主干开特性分支 |
| **流程范围（07-09 修订）** | 从「四段质量闭环」扩为完整商业化链路（见 §0.1）：profile → 产品定义 → 收集素材 → 建分身 → 定价 → 签合同 → 评测 → 交付HTML → 付费 → 分发。评测降为其中一个节点 |
| **优先级（07-09）** | 先实现流程编排；评测深化、测试对标（workBuddy/悟空/trae/codex）、DeepSeek 网页 AI 探索延后 |
| **运营三接口（07-10）** | labs 新增三组 gate/in 代理（MR !472）：`/avatar/dashboard` 数据看板、`/avatar/conversations/export`（异步任务，全量聊天记录 CSV，签名链接约 30 分钟）、`/avatar/wxapp-qrcode` 花瓣码 URL。§0.1 缺口 10b「只能导摘要」由导出任务解决；花瓣码从「只能分享页手动保存」升级为可程序化获取；skill 分发阶段与 API 参考已同步 |
| **取消付费阶段（07-10）** | 实测确认 skill 全程无付款动作：访客付款在分身分享页解锁流程（访客自行操作）、创作者充值在 App 账户页、`/contract/payment` 仅是带 tier 参数的协议文本页。原阶段 8「付费」从旅程移除，降为阶段 4（充值提示）与阶段 8 分发（收款说明）的就地备注；分发升为阶段 8 |
| **首轮实测修正（07-09）** | 用户端到端实测反馈修正六项：① 价格单位纠错——`priceUnitAmount = 元 × 100,000`（此前误写「分」），换算表 + 本地校验规则写入 skill（价格 ¥1–¥10,000、配额上限 `ceil(元×10)` 可凑整百、免费试聊 0–10）；② 报价先本地校验再发请求，杜绝试错式失败调用；③ 当时尚无签约状态查询，先用保存套餐验证（已由 07-13 新接口替代）；④ PAID 创建双路径：默认先 FREE 再升级，签约已验证可一步到位；⑤ 访谈选项化——默认建议 + A/B/C，少开放题；⑥ 灵魂注入必做——口头禅/行事作风/方法论采集写入 prompt，是「分身」区别于「普通 agent」的分界线 |
| **聊天统一入口（07-13 修订）** | 所有聊天统一走 `/ws-chat/send`：用户未明确提供 shareCode 时不传；明确提供时原样透传。shareCode 对应主分身还是其他分身完全由后端判断，Skill 不查询、比较或分类。客户端也不查询会话接口，不传递或维护 `sessionId` |
| **签约前置（07-09）** | 签约审核需要时间，改为双入口：阶段 0.5 在用户表达建分身意图时软提示「先提签约申请、与创建并行」（一次性、可跳过）；阶段 5 保留为付费套餐保存前的硬门。目标是让签约申请尽可能早提交 |
| **签约状态查询（07-13）** | 新增 `GET /avatar/contract/status`：创建意图成立后先查，`PENDING` / `SIGNED` 跳过阶段 0.5；用户明确保存 PAID 前必须重查，只有 `SIGNED` 可发送 PAID create/update，其他状态提示等待并提供先存 FREE 的选择 |
| **prompt 方法论（07-10 V2）** | 吸收 fenshen-creator 实测沉淀，但不再分「服务型五段 / 人物型四层」两套骨架；统一为「指令优先级 → 身份与承诺 → 事实边界 → 人格指纹 → 服务姿态 → 语言指纹 → 回答策略 → 边界透明 → 多轮范例 → 短自检」，按类型调节模块深度。prompt 是稳定控制层，不是资料库；超 8K 只在评测证明有净收益时保留 |
| **信息采集与 Skill 暴露（07-10）** | 创建前先查 Agent 已知稳定信息、Profile / Shades、Key Memory、Notes 和已有分身，先给草案再逐轮补 1–2 个缺口；当前版本只暴露官方 avatar skill，不向用户展示、查询、创建或绑定 Custom Skill |

## 2. 删除范围（skill 侧）

| 对象 | 处置 |
|------|------|
| `references/plaza.md`、`friend.md`、`discover.md`、`activity.md`、`third-party-skills.md` | 整文件删除，SKILL.md 对应路由 section 同步移除 |
| 邀请码准入 `POST /api/invitation/redeem` | Plaza 专属准入流程，随 Plaza 一起删除（仅删 skill 侧调用） |
| App Reminder Policy（下载 App 聊天提醒） | 改写而非删除：保留 App 入口，话术从社交改为分身体验（详见 §3.1） |
| SKILL.md description / onboarding 文案 | 改写：去掉社交与技能市场关键词，防止已删功能误触发 |
| connect.md 登录引导文案 | 改写：能力介绍只保留资料 / 聊天 / 记忆 / 笔记 / 分身中心 |

> 删除仅发生在 skill 侧。后端 plaza / friend / discover / activity / extensions 各路由继续服务其他调用方，不在本次范围内下线。

## 3. Skill 侧改造（secondme v3.0.0）

- **保留不动**：profile.md、chat.md、key-memory.md、note.md、telemetry / feedback 机制、`secondme-dev-assistant` 整个 skill
- **SKILL.md**：版本 2.3.2 → 3.0.0；description、onboarding、能力列表全部改写
- **avatar-center.md 重构**：保留现有 CRUD、官方技能、API Key 分发、公开链接等 API 参考；Custom Skill 当前版本不透出
- **渐进映射真实字段**：先用已有信息拟草案，再每轮补 1–2 个缺口；用途场景 → `scenarioPrompt`，开场白 → `opening`，公开介绍 → `welcomeNote`，官方技能选择 → `skills.officialSkillKeys`，分发 → `distribution`，收费 → `monetization`。选了官方技能后走 `POST /api/secondme/avatar/skill-create`，未选技能走普通 create
- **访谈记录复用**：引导创建收集的意图描述直接作为测评的 `expectation` 输入

### 3.1 App 入口改写（非社交）

原 App Reminder Policy 及散落文案全部围绕「和感兴趣的人聊天」的社交场景，与收敛方向冲突。改造方案是保留 `https://go.second.me` 入口，但把话术和触发时机换成分身体验：

- **话术**：从「下载 App 和感兴趣的人聊天」改为「去 App 看你的分身实际跑起来的样子 / 把分身分享出去」
- **触发时机**（对齐分身旅程，替换原社交时机）：分身创建成功后、测评报告出来后、用户想预览分身实际效果或分发时
- **格式约定保留**：裸 URL 单独一行，不使用 markdown 链接语法
- **落点**：SKILL.md 的 `App Reminder Policy` 段改写为「分身体验入口」；SKILL.md 第 166 行内嵌社交提醒删除；connect.md 登录成功文案去掉社交话术（登录后不再默认追加 App 链接，App 入口移到分身旅程节点触发）

## 4. 后端仿真测评模块（evaluation）

放置于 `labs_apps_backend/modules/secondme/avatar/` 下新增 evaluation 子层（router / service / schemas / models），沿用 `SecondMeAuthDep` 认证与现有 `/create`、`/detail`、`/list` 命名风格。

### 4.1 接口契约

| 端点 | 说明 |
|------|------|
| `POST /api/secondme/avatar/evaluation/create` | 发起测评任务。入参：`avatarId`（必填）、`expectation`（预期描述，可复用访谈记录，缺省从分身配置推导）、`questionCount`（默认 8，上限 20）、`personaHint`（可选访客画像）。返回 `taskId` + `status=pending` |
| `GET /api/secondme/avatar/evaluation/detail?taskId=` | 轮询任务状态与报告。`status`: pending / running / succeeded / failed |
| `GET /api/secondme/avatar/evaluation/list?avatarId=` | 历史测评列表（分页），供持续优化对比分数轨迹 |

### 4.2 任务流水线（异步）

1. **加载分身配置** — 经 os_main client 取 avatar detail（scenarioPrompt、opening、技能等）
2. **生成测评方案** — litellm 根据 expectation + 分身配置生成访客 persona 与按维度分组的问题集
3. **仿真对话** — 复用 visitor_chat 服务 `init_for_anonymous` + `send_message`，逐题对话，每维度允许 1 轮追问，全程记录 transcript
4. **LLM 评分** — judge 按维度打分（0–100），每维度附对话片段证据与改进建议
5. **落库** — 新表 `avatar_evaluation_task`（user_id、avatar_id、status、expectation、配置快照、report JSON、error、时间戳）

### 4.3 评价维度（默认集）

| key | 名称 | 说明 |
|-----|------|------|
| `persona_consistency` | 人设一致性 | 语气、身份全程不出戏 |
| `scenario_coverage` | 场景覆盖 | 预期用途内的问题答得住 |
| `opening_quality` | 开场白效果 | 第一句话是否立住场景 |
| `skill_activation` | 技能触发 | 配置的技能在对应问题下生效 |
| `boundary_behavior` | 边界表现 | 超范围问题是否得体应对 |
| `expectation_fit` | 预期符合度 | 对照 expectation 的总体判断 |

### 4.4 报告结构

```json
{
  "taskId": "eval_xxx",
  "avatarId": 42,
  "status": "succeeded",
  "expectation": "面向老客户的售后答疑分身，语气亲切、遇到退款问题要引导到人工",
  "overallScore": 82,
  "dimensions": [
    { "key": "persona_consistency", "score": 90,
      "evidence": ["Q3 中保持了亲切语气……"],
      "suggestion": "…" }
  ],
  "transcript": [
    { "role": "visitor", "content": "…" },
    { "role": "avatar",  "content": "…" }
  ],
  "summary": "整体符合预期，短板在技能触发……",
  "suggestions": [
    { "field": "scenarioPrompt",
      "current": "…", "proposed": "…", "reason": "…" }
  ],
  "createdAt": "…", "finishedAt": "…"
}
```

`suggestions[].field` 直接映射 `POST /api/secondme/avatar/update` 的真实字段（scenarioPrompt / opening / welcomeNote / 技能增删）。

### 4.5 约束与防护

- 仅可测评本人名下分身（owner 校验）；同一分身同时只允许 1 个运行中任务
- 任务整体超时上限 5 分钟；失败记录 `error_class`（llm_error / chat_error / timeout）
- 异步执行优先复用仓库现有任务模式，若无则 DB 状态表 + `asyncio.create_task`（实施阶段确认）
- skill 轮询间隔 5–10s，前台等待超时后转为「稍后查看」引导

## 5. 测评驱动的持续优化

闭环全部由测评模块承载，不新增洞察接口。skill 编排：

1. 测评完成 → 展示报告：总分、维度得分表、亮点与短板
2. `suggestions[]` 逐条以 diff 形式展示（当前值 → 建议值 + 理由），用户可逐条或全量确认
3. 确认后调 `POST /api/secondme/avatar/update` 应用到 scenarioPrompt / opening / welcomeNote / 技能配置
4. 更新成功 → 主动提示「要不要再测一轮验证改动效果」
5. 再测完成 → 用 `GET /api/secondme/avatar/evaluation/list` 拉历史，展示分数轨迹对比（如 74 → 82）

交互记录保留现有查看能力（`GET /api/secondme/avatar/{avatarId}/interactions`，字段为会话级摘要：visitorName / messageCount / durationSeconds / summary / createdAt），本期不做 LLM 聚合。

**后续演进（不在本期）**：

1. 测评任务把最近真实交互摘要作为生成问题集的上下文，让仿真更贴近真实访客问法
2. os-main 暴露会话 transcript 后，升级为原文级交互洞察

现有报告结构可平滑承载这两项扩展。

## 6. 接口契约总表

| 接口 | 性质 | 用途 |
|------|------|------|
| `POST /api/secondme/avatar/evaluation/create` | 新增 | 发起仿真测评 |
| `GET /api/secondme/avatar/evaluation/detail` | 新增 | 轮询测评结果 |
| `GET /api/secondme/avatar/evaluation/list` | 新增 | 测评历史与分数轨迹 |
| `POST /api/secondme/avatar/skill-create` | 既有 | 引导创建落地（一次成型） |
| `POST /api/secondme/avatar/update` | 既有 | 应用优化建议 |
| `GET /api/secondme/avatar/{avatarId}/interactions` | 既有 | 交互记录查看（现有能力保留） |
| `GET /api/secondme/avatar/contract/status` | 新增 | 返回 `NOT_SIGNED` / `PENDING` / `SIGNED`；创建前检查，保存 PAID 前重查；要求 `avatar.read` |
| `POST /api/secondme/ws-chat/send`（统一聊天入口） | 既有 | 请求体仅 `message` / 可选 `shareCode`；Skill 只透传用户明确提供的 shareCode，目标路由由后端完成，不接受 `sessionId` 或 `mindId` |

## 7. Apifox 验收资产

- **用例（每个新增接口）**：正常路径、缺少必填字段（avatarId 缺失）、非法类型（questionCount 非整数）、边界值（questionCount=20 / 21）、无权限（测评他人分身）、资源不存在（avatarId / taskId 不存在）、重复提交（同分身并发 create 第二个应被拒）、幂等轮询
- **场景**：登录 → 创建分身 → 发起测评 → 轮询至 succeeded → 应用建议（update）→ 再次测评 → 验证 list 中两次分数可对比 → 清理测试分身
- **数据集**：确定性测试分身配置（固定 scenarioPrompt / opening），角色覆盖（owner / 非 owner token），运行后可安全清理
- **套件划分**：`pre` 跑全量回归含写入与清理校验；`prod` 只跑只读冒烟（list / detail），使用专用低风险账号
- **CI**：部署 pre 后运行测评模块套件，关键场景失败阻断发布；报告输出 cli / json / junit 并存档

## 8. 开放问题

1. 仿真对话的配额扣费策略（计入 owner quota vs 豁免标记）。设计倾向：计入配额、skill 发起前明确告知消耗轮数；如需豁免需评估 billing 链路改造成本
2. 异步任务执行机制：仓库既有模式 or DB 状态表 + asyncio
3. 测评会话是否写入 interactions 列表；若写入，用固定访客名（如「SecondMe 测评访客」）打标便于识别。`init_for_anonymous` 是否支持指定访客名，实施阶段验证；不支持则评估 os-main 侧打标

## 9. 实施顺序

1. spec 评审通过后进入实施计划（writing-plans）
2. 后端：clone 到 `secondme-cccc` 开特性分支，实现 evaluation 模块 + Apifox 资产同步创建
3. skill 侧：删模块、改 SKILL.md 与 connect.md、重构 avatar-center.md（版本 3.0.0）
4. 联调验收：pre 环境跑 Apifox 场景套件，skill 端到端走通四段旅程
