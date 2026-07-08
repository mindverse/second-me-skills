# 分身中心改造设计：从全功能入口到分身工场

- 日期：2026-07-08
- 状态：设计已对齐，待评审
- 范围：second-me-skills（skill 侧） + secondme 后端 `biz/labs_apps_backend`（服务侧）
- 版本影响：`secondme` skill 2.3.2 → 3.0.0（破坏性收窄）

## 0. 背景与目标

现有 `secondme` skill 覆盖登录、社交、记忆、技能市场等十余个模块，其中 Plaza、好友、发现、动态、第三方技能后续不再需要。改造后 skill 收窄为「个人账户 + 分身工场」：保留基础模块，把重心放到帮用户更好更快地创建分身，并持续把它调优到符合预期。

核心闭环：

```
① 引导创建 → ② 仿真测评 → ③ 建议确认与应用 → ④ 再测对比
                    ↺ 循环直到符合预期
```

- ① 引导创建：访谈式提问，自动组装创建参数，替代裸字段填表
- ② 仿真测评：后端模型扮演访客与分身真实对话，按维度评分出报告
- ③ 建议确认：报告自带优化建议，diff 展示，用户确认后一键应用到 prompt
- ④ 再测对比：应用后提示再测一轮，分数轨迹对比验证改进

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

## 2. 删除范围（skill 侧）

| 对象 | 处置 |
|------|------|
| `references/plaza.md`、`friend.md`、`discover.md`、`activity.md`、`third-party-skills.md` | 整文件删除，SKILL.md 对应路由 section 同步移除 |
| 邀请码准入 `POST /api/invitation/redeem` | Plaza 专属准入流程，随 Plaza 一起删除（仅删 skill 侧调用） |
| App Reminder Policy（下载 App 聊天提醒） | 主要服务社交场景，整段删除 |
| SKILL.md description / onboarding 文案 | 改写：去掉社交与技能市场关键词，防止已删功能误触发 |
| connect.md 登录引导文案 | 改写：能力介绍只保留资料 / 聊天 / 记忆 / 笔记 / 分身中心 |

> 删除仅发生在 skill 侧。后端 plaza / friend / discover / activity / extensions 各路由继续服务其他调用方，不在本次范围内下线。

## 3. Skill 侧改造（secondme v3.0.0）

- **保留不动**：profile.md、chat.md、key-memory.md、note.md、telemetry / feedback 机制、`secondme-dev-assistant` 整个 skill
- **SKILL.md**：版本 2.3.2 → 3.0.0；description、onboarding、能力列表全部改写
- **avatar-center.md 重构**：保留现有 CRUD、自定义技能、API Key 分发、公开链接等 API 参考；新增四段式旅程编排
- **访谈映射真实字段**：用途场景 → `scenarioPrompt`，开场白 → `opening`，公开介绍 → `welcomeNote`，技能选择 → `skills`（官方 / 已有自定义 / 新建 Markdown），分发 → `distribution`，收费 → `monetization`。访谈完成后走 `POST /api/secondme/avatar/skill-create` 一次成型
- **访谈记录复用**：引导创建收集的意图描述直接作为测评的 `expectation` 输入

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
