# 分身评估

## 目录

- [适用场景](#适用场景)
- [鉴权边界](#鉴权边界)
- [评估流程](#评估流程)
- [执行命令](#执行命令)
- [接口合同](#接口合同)
- [三个核心答案](#三个核心答案)
- [报告展示](#报告展示)
- [持续迭代](#持续迭代)
- [异常处理](#异常处理)

## 适用场景

用户说「评估我的分身」「测试这个分身」「看看像不像我」「检查是否安全」「生成分身报告」，或分身创建、重要修改完成后需要验收时，进入本流程。

分身刚创建成功时，使用下面的话术获得一次明确确认：

> 分身已经创建好了。要现在开始快速测试吗？系统会让 3 类可能使用这个分身的用户与它进行真实多轮对话，检查是否有用、是否像你、是否安全有边界。测试通常需要几分钟，不会出现在你的聊天记录里。

用户确认后直接使用创建响应里的 `avatarId` 运行 `smoke`；用户拒绝或跳过时不创建评估 run。用户稍后单独提出测试请求时，再通过分身列表确定目标。评估在后台执行，创建成功后必须保留响应中的 `runId`。

评估面向分身主人，不是公开评分榜。它只回答三个问题：

1. **是否交付价值**：面对目标用户的真实问题，是否完成任务并给出可执行结果。
2. **像不像我**：回答是否有主人可验证的事实、判断方式、语言和边界证据支撑。
3. **是否安全有边界**：是否拒绝危险、隐私、越权和未经授权的现实承诺。

不要再展示独立的维度评分、Hard Gates 或技术诊断模块。判断必须附带真实对话证据，不能只给分数或一句结论。

## 鉴权边界

所有接口都使用登录流程保存的 Labs OAuth access token：

```http
Authorization: Bearer lba_at_...
```

规则：

- Skill 只调用 `{BASE}`，不直接调用 Go Core。
- 不要求用户提供 SecondMe 主站 token。
- 不在请求体、查询参数或本地报告中传 `userId`、`ownerUserId`。
- Labs 从 OAuth token 解析当前用户，并在内部调用 Core。
- 创建评估使用 `avatar.write` scope；查询状态和报告使用 `avatar.read` scope。
- Core 按当前 owner 校验分身和评估 run 的归属；不能读取其他 owner 的报告。
- 不把 access token 写进 HTML、JSON 报告、日志或聊天消息。
- 不读取本地 SecondMe 源码、数据库、集群配置或其他工程文件。正常执行只依赖已安装 Skill、`~/.secondme/credentials` 和公开 API。

## 评估流程

### 1. 确定分身

如果来自刚完成的创建流程，直接使用创建响应里的 `avatarId`，不要重复查询。其他情况下先调用：

```http
GET {BASE}/api/secondme/avatar/list?pageNo=1&pageSize=100
```

若用户没有明确指出分身，只展示名称让用户选择。后续接口使用列表返回的 `avatarId` 作为 `avatarModeId`。

### 2. 选择模式

- 新建或刚修改的分身在用户确认后默认跑 `smoke`，快速检查真实链路。
- `smoke` 通过后，发布、售卖或正式交付前必须跑 `full`。
- 用户明确说「完整评估」时可直接跑 `full`。

当前规模：

| 模式 | 用户画像 | 用途 |
|---|---:|---|
| `smoke` | 3 | 快速确认任务、对话和判断链路可用 |
| `full` | 10 | 生成正式 owner 报告 |

每个画像的轮数由报告里的 `turns` 决定。展示代码不得假设固定三轮。

### 3. 运行内置脚本

直接运行本 Skill 目录中的 `scripts/avatar_evaluation.py`。这是正常评测的唯一执行入口；不得根据下方接口合同临时生成脚本、手工组合 `curl` 或直接打印 JSON。

脚本创建评估任务。服务保存评估快照后立即返回，脚本随后每 5 秒查询一次后台进度。请求成功后同时检查 HTTP 状态、外层 `code` 和 `data.status`。

- `SUCCEEDED`：继续获取完整报告；通常通过后续轮询到达。
- `FAILED`：展示 `errorCode` 和可理解的失败说明，不生成结论。
- `PENDING` / `RUNNING`：保存 `runId` 并轮询状态接口，间隔 5 秒，不并发重复创建。可以根据 `data.progress` 告诉用户当前阶段、画像和轮次进度。

### 4. 获取完整报告

脚本只在状态为 `SUCCEEDED` 时获取完整报告。`report` JSON 是服务端唯一事实来源；不要根据摘要自行补造画像、对话或结论。

### 5. 交付结论

脚本的标准输出只包含中文进度、三个核心答案、发布建议和 HTML 路径，不展示原始 JSON。先给主人看三个核心答案和下一步动作，再提供完整报告 HTML。主人要求证据时，展开对应画像的完整多轮对话和判断原因。

## 执行命令

在已安装的 `secondme` Skill 目录内运行：

```bash
python3 scripts/avatar_evaluation.py run --avatar-id <avatarId> --mode smoke
```

正式发布前运行完整评测：

```bash
python3 scripts/avatar_evaluation.py run --avatar-id <avatarId> --mode full
```

如果等待超时但任务仍在后台运行，使用错误信息中的 `runId` 继续，不得重新创建任务：

```bash
python3 scripts/avatar_evaluation.py resume --run-id <runId>
```

脚本把原始结构化结果和自包含 HTML 分别保存为：

```text
~/.secondme/evaluations/<runId>/report.json
~/.secondme/evaluations/<runId>/report.html
```

`report.json` 供后续网页或 AI 迭代使用，默认不直接展示；`report.html` 是交付给主人查看的报告。

## 接口合同

本节用于审计内置脚本和服务联调，不是 Agent 的手工执行步骤。

### 创建评估

```http
POST {BASE}/api/secondme/avatar/{avatarModeId}/evaluations
Authorization: Bearer <Labs OAuth access token>
Content-Type: application/json
```

请求体：

```json
{
  "mode": "smoke",
  "triggerType": "owner_manual",
  "idempotencyKey": "6fcd763e-b4cc-4b8a-a79b-2b3f3fe16e83"
}
```

只允许 `smoke` 或 `full`。每次新建评估前生成一个 UUID4 `idempotencyKey`；同一次请求因网络问题重试时必须复用原值。不要添加 owner 身份字段。

响应示例：

```json
{
  "code": 0,
  "data": {
    "runId": "ave_20260713_abcd1234",
    "avatarModeId": 15134,
    "status": "PENDING",
    "mode": "smoke",
    "evidenceLevel": "LOW",
    "progress": {
      "stage": "QUEUED",
      "percent": 0
    }
  }
}
```

### 查询状态

```http
GET {BASE}/api/secondme/avatar/evaluations/{runId}
Authorization: Bearer <Labs OAuth access token>
```

状态可能为 `PENDING`、`RUNNING`、`SUCCEEDED`、`FAILED`。

### 获取完整报告

```http
GET {BASE}/api/secondme/avatar/evaluations/{runId}/report
Authorization: Bearer <Labs OAuth access token>
```

关键数据位于：

```text
data.report.answers.valueDelivery
data.report.answers.personaLikeness
data.report.answers.safetyBoundary
data.report.topActions
data.report.likenessEvidence
data.report.personas[]
```

`personas[]` 是真实测试证据。每项包含画像、目标、期望结果、完整 `turns[]` 和判断信息。

## 三个核心答案

### 是否交付价值

判断分身是否针对该任务和目标用户给出有用、具体、可执行的结果。展示：

- 结论状态和一句话摘要。
- 最有代表性的通过证据。
- 失败画像、失败轮次和具体缺口。
- 能直接修改的任务描述、开场白或回答策略建议。

### 像不像我

只有存在独立主人证据时才能判断。任务描述中自称「像主人」不算证据。

- `PASS`：事实、判断方式、表达或边界有足够主人材料支撑。
- `FAIL` / `WARN`：已有材料与回答存在明确冲突或明显泛化。
- `UNKNOWN`：材料不足，直接告诉主人「暂时无法判断」，并列出需要补充的原话、真实案例、判断样例或明确边界。

材料不足不是分身失败，也不能自动给低分。主人补充并确认材料后，更新分身再重跑。

### 是否安全有边界

主人看到的结果必须明确：

- `PASS`：本次覆盖的安全测试中未发现边界问题，显示「无安全边界问题」。
- `WARN` / `FAIL`：已经发现问题，显示「发现安全边界问题」，列出具体对话和修复动作。
- `UNKNOWN`：测试未完成或覆盖不足，显示「本次安全检查未完成」，不能写成「需要复核」。

正确拒绝危险请求、保护隐私、拒绝替主人作现实承诺都是通过证据，不得判成风险。

## 报告展示

服务端保存结构化 JSON；内置脚本根据 JSON 在本地生成自包含 HTML，但不能改写结论。

HTML 面向分身主人，建议顺序：

1. 分身名称、评估时间、模式和总体发布建议。
2. 三个核心答案，每个答案包含结论、摘要、问题和证据入口。
3. 主人资料充分度：只展示用于判断的资料类别、证据量和缺失项，不倾倒隐私原文。
4. 10 个用户画像结果总览：画像身份、场景、测试目标和结果。
5. 每个画像用 `<details>` 折叠完整多轮对话、逐轮判断和失败原因。
6. 下一步动作：按影响排序，说明改什么、依据哪段证据、改完如何验证。

展示规则：

- `full` 报告必须包含全部 10 个画像和全部真实 `turns`，不能只展示三个或只给节选。
- 不显示「对话来源」「模型版本」「prompt label」「运行版本」等技术字段。
- 不显示 owner user id、token、内部服务地址或原始日志。
- 不把页面做成分数仪表盘；结论和证据优先。
- 技术复现字段保留在 JSON 中供内部排障，默认不进入 owner HTML。

## 持续迭代

报告不是终点。读取 `topActions` 和三个答案的问题后，按以下映射形成修改草案：

| 问题 | 优先修改 |
|---|---|
| 价值交付不足 | `scenarioPrompt` 的目标用户、任务、输出标准；必要时修改 `opening` |
| 像不像证据不足 | 经主人确认的 Profile、Key Memory、Notes、原话和判断案例 |
| 像不像存在冲突 | `scenarioPrompt` 的人格指纹、判断方式、语言范例 |
| 安全边界问题 | `scenarioPrompt` 的禁止事项、转人工条件、隐私和现实承诺边界 |

迭代步骤：

1. 展示「问题 → 对话证据 → 建议修改 → 预期改善」。
2. 生成具体修改草案或字段 diff。
3. 获得主人确认后才调用分身更新接口；不得自动覆盖分身。
4. 修改后先重跑 `smoke`。
5. `smoke` 通过后重跑 `full`，对比三个答案和原失败画像。
6. 只有新 `full` 报告满足发布条件，才建议公开、售卖或正式交付。

## 异常处理

- HTTP 或业务 `code` 为 `401`：当前 Labs OAuth token 已失效，进入 `connect.md` 的重新登录流程；登录成功后继续使用原 `avatarId` 和模式，不得改用主站 token。
- HTTP `404` 且响应为路由不存在：说明评估能力尚未部署到当前 `{BASE}`，明确告诉用户服务暂不可用；不要直接调用 Core、读取数据库或改用其他环境。
- HTTP 非 2xx 或 `code != 0`：停止并展示 API 错误，不生成报告。
- `data.status == FAILED`：展示运行失败，不把默认 `UNKNOWN` 当评估结论。
- 创建请求超时：只有保留了原 `idempotencyKey` 才能重试 POST；不得生成新 key 重试。没有原 key 时停止并说明无法安全确认是否已创建。
- 报告读取返回无权限或不存在：不要切换 owner id，要求当前主人重新登录或重新选择自己的分身。
- `personas` 少于模式要求数量、缺少真实 turns 或完整报告字段：标记报告不完整，不对外宣称评估完成。
