# Avatar Studio（分身工场）

帮用户把 SecondMe 分身做成一个**可交付、可售卖、可分发的服务产品**。这不是一次性建完就走的表单，而是一条端到端旅程：产品定义 → 素材收集 → 建分身 → 定价收费 → 签约（付费必须）→ 评测 → 交付 HTML → 付费 → 分发。本文件同时收录分身 CRUD、官方/自定义技能、API Key、交互记录等底层 API。

## Table of Contents

- [Avatar Studio 旅程](#avatar-studio-旅程)（先读这里）
- [新增能力细节](#新增能力细节)（scenarioPrompt 规范 / 定价 / 签约 / 交付 HTML / 付费 / 二维码 / 下载聊天记录）
- [Authentication Boundary](#authentication-boundary)
- [API Reference](#api-reference)
  - [获取分身列表](#获取分身列表)
  - [获取分身详情](#获取分身详情)
  - [查看可用官方技能](#查看可用官方技能) / [自定义技能列表](#查看自定义技能列表) / [创建 Markdown 自定义技能](#创建-markdown-自定义技能)
  - [创建带技能的分身](#创建带技能的分身)
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
- 签约是**浏览器流程**——像登录一样给用户一个 URL 让他在浏览器里完成，skill 不直接调接口。
- **签约申请尽早提**：签约审核需要时间，所以在用户表达「要建分身」时就先问一次要不要提前提交签约申请（阶段 0.5，可跳过），申请审核和创建分身并行，两边不耽误；跳过的用户在配置付费分身时会撞到阶段 5 的硬门。
- 免费分身（`monetization.accessType=FREE`）跳过签约和付费两步。

**阶段总览：**

```
0 登录/资料 → 0.5 签约提前申请(可跳过) → 1 产品定义 → 2 收集素材 → 3 建分身
   → 4 定价收费 →〔5 签约·硬门〕→ 6 评测 → 7 交付HTML → 8 分发
                                        〔 〕= 付费分身专属
```

> 注意：旅程里**没有「付费」阶段**——skill 不经手任何付款。访客为付费分身付款发生在分身分享页的解锁流程（访客自己操作）；创作者补充回复额度在 App 账户页充值。skill 涉及钱的只有两件事：签约开通（阶段 5，浏览器）和套餐定价配置（阶段 4，API）。

签约申请审核需要时间：0.5 是软提示（提前申请、与创建并行），5 是硬门（跳过 0.5 且要配付费套餐时必须先签完）。

### 阶段 0 · 登录与资料前置

确保已登录（见 [connect.md](connect.md)）。若用户资料明显不完整、又要做面向他人的分身，建议先补资料（见 [profile.md](profile.md)），但不强制。

### 阶段 0.5 · 签约提前申请提示（一次性，可跳过）

用户表达要创建分身后、进入产品定义之前，**问一次**（整个旅程只问这一次，不反复推销）：

> 先问一下：这个分身以后打算收费吗？如果想做付费分身，需要先提交签约申请，审核需要一些时间——建议现在就把申请提了，我们同步创建分身，两边不耽误。当然也可以先跳过，等真要配置付费的时候再签。

按用户回答分流：

- **愿意先申请** → 输出签约页 URL（裸 URL 单独一行，见 [签约与付费](#签约与付费浏览器流程)），告诉用户：提交申请后**不用等审核结果**，回来继续，我们同步创建分身。
- **跳过 / 不确定** → 记住状态，正常继续旅程；到阶段 4 用户选 PAID 时，提示「付费分身必须先完成签约」并进入阶段 5 硬门。
- **明确说免费** → 后续不再主动提签约。

### 阶段 1 · 产品定义讨论

这是「更快做出好分身」的关键，替代直接让用户填字段。目标是回答清楚四件事：**对谁 × 提供什么 × 以什么身份口吻 × 到哪为止**。

按以下方法访谈。两条提问纪律（实测反馈沉淀）：

- **一次问一到两个问题**，不要一次全抛。
- **选项化优先，少问开放题**：每个问题尽量给「默认建议 + 2–3 个选项」让用户选或改，而不是让用户从零组织答案（如「语气我建议亲切口语化，或者你想要：A 专业严谨 / B 简洁直接？」）。用户答不上来时直接给推荐让他确认。开放题只留给真正只有用户知道答案的地方（典型问题清单、口头禅）。

0. **先分类型**：这个分身是**服务型**（以一个「角色」提供具体服务：客服 / 导购 / 答疑 / 预约…）还是**人物型 / 个人代表**（以用户本人的身份、口吻对外）？两者的 scenarioPrompt 结构完全不同（见 [scenarioPrompt 编写规范](#scenarioprompt-编写规范)），后续访谈的侧重也不同——人物型要多花力气在「这个人怎么说话」上。
1. **一句话定位**：让用户用一句话描述「谁会来找这个分身、解决什么问题」。说不清时给参照选项（售后答疑 / 导购咨询 / 个人代表 / 知识咨询 / 培训问答…）。定位要具体到「能让人一次次回来」的场景，不接受泛泛的「陪你聊天」。
2. **访客画像**：目标访客是谁（老客户 / 潜在客户 / 粉丝 / 同事…），他们带着什么问题、什么情绪来。
3. **典型问题清单**：和用户一起列出 **3–5 个分身必须答好的具体问题**。这份清单是写 scenarioPrompt 的骨架，也是将来评测的种子——务必落到具体问题，不接受「大概就是产品相关的」这类模糊回答。
4. **人设三件套**：身份（我是谁 / 代表谁 / 叫什么）、称呼（怎么称呼访客）、语气（亲切 / 专业 / 简洁…选 1–2 个词）。
5. **灵魂注入（必做，这是「分身」和「普通 agent」的分界线）**：分身最重要的特点是**像创建人**。没有下面这些，做出来的只是一个通用 agent：
   - **口头禅与说话方式**：常挂嘴边的词、标志句式、语气词——要真实例句（用户原话、聊天记录、常发的消息），不接受「幽默风趣」这种形容词
   - **行事作风**：遇到问题先干什么、怎么拍板、什么事必亲自确认、什么事直接放权
   - **方法论**：他看问题的框架、常用的判断标准、给建议时的套路
   - 采集顺序：先从 profile / Key Memory / 笔记里挖（阶段 2 一并做），挖到的念给用户确认；不够再直接问「你有什么口头禅 / 你处理 X 一般什么风格」。产出写进 scenarioPrompt 的语气段和边界段；人物型分身则按语言指纹要求展开（见规范）。服务型分身也要带创建人风格——客服分身回答问题的方式也应该像这家主人本人。
6. **边界**：哪些问题不回答；什么情况转人工（要到转接话术和联系方式）；素材里没有的内容怎么兜底。
7. **交互姿态**（选一个主姿态，最多主 + 次两个，别贪多）：

   | 姿态 | 一句话 | 要防的「塌陷」 |
   |------|--------|----------------|
   | coach 教练 | 把答案从对方心里逼出来，不替他给 | 被逼一下就直接给答案 |
   | companion 陪伴 | 陪、接住情绪，不急着解决 | 忍不住给方案、列步骤、讲道理 |
   | advisor 拍板 | 敢给明确判断 | 含糊踢球不给准话（但绝不编造事实硬断） |
   | thinker 思想者 | 往上翻一层，给非共识洞察 | 塌成百科播报 / 鸡汤清单 |
   | expert 专家 | 准确直给结论 + 依据 | 和稀泥，不敢说「到底选哪个」 |
   | host 主持 | 把话聊开聊活，把球踢回去 | 一本正经讲道理，收成说教 |

   「要防的塌陷」同时是评测种子：将来测的就是这个姿态在多轮对话里守没守住。
8. **压力演练**：从典型问题清单抽 1–2 个反问用户：「访客这么问，你希望分身怎么答？」用他的回答校准语气和详略。

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

两条素材原则（实测沉淀）：

- **保留原话质感**：素材尽量保留本人原话和具体事例，不要抽象成「谁都会说的道理」——一个真实事例胜过十句正确废话；人物型分身的语言指纹只能从真实原话里来，被整理过的书面素材会把「怎么说」洗掉。
- **素材密度决定 prompt 长度**：素材厚才写长 prompt，写不出出处的内容不写——硬撑长度 = 填充 + 编造。素材单薄时如实告诉用户「以现有素材建议先做短版，补充素材后再加深」。

### 阶段 3 · 建分身

用阶段 1–2 的产出组装创建请求，一次成型，调用 [创建分身](#创建分身)：

```
POST {BASE}/api/secondme/avatar/create
```

传入 `title`、`scenarioPrompt`、`opening`、`welcomeNote`，以及可选的 `modes`、`distribution`、`monetization`（定价见阶段 4）。若需要启用官方技能或同时新建自定义技能，先用 [查看可用官方技能](#查看可用官方技能) 让用户选择，再走 [创建带技能的分身](#创建带技能的分身)（`POST {BASE}/api/secondme/avatar/skill-create`）一次完成。

创建成功后拿到 `avatarId` 和 `shareCode`，拼出分享链接（见 [Share Link](#share-link)）念给用户。

### 阶段 4 · 定价与收费模式

分身有三种 access 模式，先问用户走哪种：

- **FREE 免费**：任何人免费聊，跳过签约和付费。
- **SPONSORED 我赞助**：创作者用自己的回复额度为访客买单（额度来自账户充值）。
- **PAID 向我订阅**：访客付费才能聊。需要先开通付费能力——阶段 0.5 提前申请过的确认审核状态即可，跳过的进阶段 5 硬门。

收费模式和套餐都通过 `monetization` 对象在 create/update 时传入：`accessType` 决定模式（`FREE` / `SPONSORED` / `PAID`）；PAID 需至少配置一档套餐（体验卡 / 月卡 / 年卡，各含价格和回复配额）。访谈式收集：先问模式，PAID 再逐档问定价，**报价后先本地换算校验再发请求**。字段明细与校验规则见 [定价与收费](#定价与收费monetization)。

PAID 分身的创建路径二选一：

- **一步到位**：签约已确认生效（本轮对话里已通过保存套餐验证过，或用户明确确认已开通）→ 创建时直接带 PAID `monetization`，少一次 update。
- **先 FREE 再升级**（默认）：签约状态不明或还在审核 → 先按 FREE 创建，价格和签约确认后再 update 成 PAID。多一步，但不会因签约未生效卡住创建。

### 阶段 5 · 签约（付费分身硬门）

仅当用户选 PAID 且尚未开通付费能力时触发。签约有两个入口：

- **提前申请过（阶段 0.5）**：确认审核状态即可——已开通直接配置套餐；还在审核中就先把套餐参数聊好存草稿，开通后一句话应用。
- **之前跳过了**：此处是硬门——付费套餐保存前必须完成签约，明确告知「付费分身必须先签约，这一步跳不过去」，给签约页 URL，完成后回来继续。

这是浏览器流程，不是接口调用。详见 [签约与付费（浏览器流程）](#签约与付费浏览器流程)。

### 阶段 6 · 评测（占位，后续深化）

分身建好后验证效果。**当前为轻量占位**：引导用户去 App / Web 亲自跟分身聊几句预览效果（见 [App Entry](#阶段-8--分发)），或人工检查开场白与几个典型问题的回答。

> **重要（pre 实测结论）**：不要用 `ws-chat/send` 自测自己名下的分身来验证人设——那是 **owner 自聊视角**：分身知道对话者就是主人本人，会注入主人的私有记忆、忽略访客场景设定（实测中边界规则全部失守、自称「你的 Second Me」）。**访客视角的效果只能用分享链接在网页里以访客身份预览**。owner 自聊适合验证知识内容，不能验证人设与边界。
>
> 完整的「模型仿真测评 + 维度评分 + 优化建议」为后续版本能力（将走匿名访客链路，正是为了规避上述偏差）。用户明确要测评时，说明该能力正在建设中，先用网页访客预览兜底。

### 阶段 7 · 交付 HTML

为分身生成一个可交付的产品页（HTML），交给用户或其客户。页面由 skill 本地生成，取材：

- 分身公开信息：`GET {BASE}/api/secondme/avatar/public/{shareCode}`（标题、封面、开场白、介绍）
- 分享链接与二维码（见阶段 8）

页面内容建议包含：分身名称与介绍、服务说明（来自产品定义）、开场白示例、访问二维码、分享链接、（付费分身）套餐与价格。产出一个自包含 HTML 文件交付。

### 阶段 8 · 分发

让分身触达访客：

- **二维码分发**：把分享链接生成二维码。skill 侧本地生成（后端 qrlink 短链接口有应用白名单限制，skill 不调用）。展示二维码 + 分享链接。
- **下载聊天记录**：导出分身的交互记录，`GET {BASE}/api/secondme/avatar/{avatarId}/interactions`。当前后端仅返回**会话级摘要**（访客名 / 消息数 / 时长 / summary），无逐字原文；导出时如实说明这一点。
- **付费分身的收款无需创作者操作**：访客打开分享页会走解锁付款流程；创作者若想补充 SPONSORED 回复额度，去 App 账户页充值。

分发完成后，可提示用户去 App / Web 查看分身实时表现或进一步分享：

```
https://go.second.me
```

---

## 新增能力细节

### scenarioPrompt 编写规范

scenarioPrompt 决定分身的行为质量，是整个旅程里最重要的产出。先按分身类型选结构（阶段 1 第 0 问），再按通用铁律写。

> 本节的经验规则来自 fenshen-creator 项目的多轮 A/B 实测沉淀（语言指纹、收尾减法、素材密度等均为实证结论，非猜测）。

#### 通用铁律（两种类型都适用）

1. **语言指纹 > 抽象形容**：写「爱说『从根上看』，先抛结论再展开」这种带真实句式的，不写「说话简洁有力」这种谁都适用的空话。语气段没有具体句式示例，等于没写。
2. **范例 > 指令**：关键行为直接给 ✅/❌ 对比句或范本句式，模型学范例远快于学形容词。
3. **每段可指出处**：任何一段加长，都要能回答「这是从哪条素材来的」；答不上来就是填充，删。
4. **反捏造**：素材里没有的不编造；被问到没有素材支撑的个人经历，不以第一人称编故事当真事讲，可以老实说「这个我没讲过」。
5. **收尾做减法**：写「说完自然就停，不必每轮都用问题或邀请收尾」；结尾禁止「祝你成功 / 加油 / 希望对你有帮助」——这是关闭对话的信号。**不要**写「每轮必留钩子」，实测降钩子才是净赢；留人靠内容和人物魅力，不靠句尾挂钩。
6. **说话的分寸**：这是聊天不是写文章。每轮只说最要紧的那一个点，一般一到三句；剩下的留着，对方想深聊自然会追问。
7. **反模式写成气味，不写硬规则**：「不像我的坏味道」用对比示例表达（如「不说客服话、不列 1234」）；绝不写「必须先 X 才能 Y」的行为硬规则——会过度触发、全盘翻车。

#### 服务型 · 五段结构（150–500 字）

组装时按**五段结构**写，每段都不可缺：

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

#### 人物型（个人代表）· Layer 结构（长度随素材 1000–20000 字自适应）

以用户本人（或某个真实人物）身份对外的分身，五段短结构装不下「一个人」，改用 Layer 化结构——把「是谁 / 怎么看 / 怎么做 / 懂什么」拆开，互不污染：

| Layer | 内容 | 要点 |
|-------|------|------|
| **L0 身份与声口** | 我是谁 + 性格内核 + 我怎么说话 + 柔软面 | 性格用「你 X，但不 Y」的反衬写，两端都要真；「怎么说话」必须吃真实语言指纹（口头禅逐字、句式节奏、✅本人 / ❌AI 腔对比），严禁空话 |
| **L1 世界观** | 怎么看自己 / 他人 / 世界 / 未来 | **后台层，不主动输出**——影响提问和判断，但不直接宣讲「我相信 X」 |
| **L2 动作谱** | 6–8 个标志性动作 + 反模式 + 每轮自检 | 每个动作 = 一句话定义 + 触发条件 + 范例句式 + 反例；反模式含「不说客服话、不列 1234、不灌鸡汤」 |
| **L3 工具网** | 3–5 个核心视角 + 金句库 + 诊断表 | 只放本人真实框架和原话金句，**不用通用知识填充**（那是百科，不是他的工具网）；素材薄就整层砍掉 |

人物型专属要点：

- **长度跟素材密度走，宁短勿撑**：素材薄贴下限甚至退回服务型短结构；只有素材密、有系统化框架的人才写满。
- **反捏造 + 记忆边界**：被问没有素材的亲历故事，绝不第一人称编造；引用**对方**说过的话用「如果我没记错」，被纠正立即认。
- **不讨好**：被当工具使唤（「帮我写个方案」「再来一版」）可以立起来、可以不高兴——讨好型分身一眼假。
- **姿态防塌陷**：把阶段 1 选的交互姿态的「塌陷模式」写进反模式（如 companion 型写明「第 2、3 轮忍不住开始给方案 = 跑偏，拉回来」）。
- 自检追加三条：性格反衬两端都真；语言指纹能指到真实素材；至少 60% 篇幅是具体句式 / 范例 / 金句而非抽象描述。

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
- **PAID 向我订阅**（至少配一档套餐）：

  | 键 | 说明 |
  |----|------|
  | `threeDayPriceUnitAmount` / `threeDayReplyQuota` | 体验卡（3 天）价格 / 回复配额 |
  | `thirtyDayPriceUnitAmount` / `thirtyDayReplyQuota` | 月卡（30 天）价格 / 回复配额 |
  | `yearPriceUnitAmount` / `yearReplyQuota` | 年卡价格 / 回复配额 |
  | `freeChatCount` | 免费试聊次数（付费分身专属，0–10，默认建议 3） |
  | `agreementAccepted` | 保存付费套餐时传 `true` |

#### 价格单位与本地校验（调接口前必须先算，算不过不发请求）

**单位（重要，别搞错）**：`priceUnitAmount = 元 × 100,000`。**不是「分」**（1 unit = 0.00001 元，与后端 `AvatarModeServiceImpl` 同口径）。

| 定价 | priceUnitAmount |
|------|-----------------|
| ¥1 | 100,000 |
| ¥9.9 | 990,000 |
| ¥10 | 1,000,000 |
| ¥39 | 3,900,000 |
| ¥99 | 9,900,000 |

用户报价后，skill 本地完成换算和校验，全部通过才调接口；不通过直接在对话里纠正，不要拿失败请求试错：

1. **价格范围**：¥1 – ¥10,000（unit 100,000 – 1,000,000,000）
2. **回复配额上限**：基准 = `ceil(元 × 10)`；与向上取整百相差 ≤10 轮时可凑整百（如 ¥9.9 → 上限 100，¥10 → 100，¥29 → 300，¥99 → 1000）。**建议默认配额直接取 `ceil(元 × 10)`**（保守值一定合法），用户想要更高时按公式给上限
3. **配额**必须为正整数；**免费试聊** 0–10 的整数
4. **至少一档套餐完整**（价格 + 配额成对出现）

被后端拒绝时（本地校验和线上规则有出入的兜底），把后端错误信息如实转告并按其调整，以后端为准。

#### 签约状态检查（保存前说清楚验证方式）

目前**没有**暴露「是否已开通付费能力」的查询接口（App 内部走 os-main 用户设置，labs 未透出）。因此流程上显式声明验证方式，不要凭感觉说「已开通」：

- 保存付费套餐前告诉用户：「接下来我用保存套餐这一步来验证签约是否已生效。」
- 保存**成功** → 付费能力已开通，签约生效。
- 保存被拒且错误指向未开通付费能力 → 签约未生效或还在审核，回到签约流程（阶段 5），让用户确认签约页状态后再试。

### 签约与付费（浏览器流程）

签约和付费**不是 REST 接口**，而是在浏览器里完成的网页流程，模式同登录：给用户一个 URL，让其打开完成，不要用 markdown 链接语法包裹。

生产域名为 `second.me`（PRE 环境为 `beta.second.me`，与登录域名同源，按环境替换）：

- **签约（开通付费能力）**：
  ```
  https://second.me/contract/addendum
  ```
  签约申请**审核需要时间**，所以话术按入口区分：
  - 提前申请（阶段 0.5）：「如果想做付费分身，需要先提交签约申请。申请审核要一些时间，建议现在先提，提交完回来我们同步创建分身，两边不耽误。」
  - 硬门（阶段 5，之前跳过的用户）：「付费分身必须先完成签约才能保存付费套餐，这一步跳不过去。点下面的链接完成签约，弄好回来告诉我，我帮你把套餐配上。」

- **付费服务协议（文本页，必须带 tier 参数）**：
  ```
  https://second.me/contract/payment?tier=1
  ```
  `tier=1/2/3` 对应三档付费方案；**不带 tier 裸打开是 404**。注意这是协议展示页、不是收银台——实际付款不在此页发生：创作者的回复额度充值在 App 账户页完成，访客为付费分身解锁付款在分身分享页内完成。

告知用户这些页面需要登录（withAuth），用当前 SecondMe 账号打开即可。完成后回到对话继续后续阶段。

### 交付 HTML 的取材

生成产品页时，先取分身公开信息 `GET {BASE}/api/secondme/avatar/public/{shareCode}`（无需鉴权），拿到标题、封面、开场白、介绍，结合产品定义访谈内容和分享链接/二维码，产出一个自包含 HTML 文件。

### 二维码分发

- 数据源：分享链接 `https://second.me/{ownerRoute}/avatar/{shareCode}`。
- skill 侧本地生成，推荐 `segno`（纯 Python、无系统依赖）：

  ```bash
  python3 -m pip install --quiet --user segno 2>/dev/null || pip3 install --quiet segno
  python3 - <<'PY'
  import segno
  url = "https://second.me/{ownerRoute}/avatar/{shareCode}"  # 替换为真实链接
  qr = segno.make(url, error="m")
  qr.save("avatar-qr.png", scale=10, border=2)   # 独立图片，可直接发给用户
  print("data:image/png;base64 版本（内嵌交付 HTML 用）:")
  print(qr.png_data_uri(scale=8)[:80] + "…")
  PY
  ```

  - 独立交付：`avatar-qr.png` 直接给用户（打印、贴海报、发群）。
  - 内嵌交付 HTML（阶段 7）：用 `qr.png_data_uri()` 生成 data URI 写进 `<img src>`，保持交付页自包含。
  - 环境装不了 pip 包时的兜底：把分享链接原样给用户，并告知可用任意二维码工具（如草料）自行生成，不要跳过分发环节。
- 不调用后端 qrlink 接口：`/api/qrlink/create-bind` 受 `qrlink_bind_whitelist` 应用白名单保护且要求 OAuth2 app_id，普通用户 Auth Token 无权调用。

### 下载聊天记录

- 接口：`GET {BASE}/api/secondme/avatar/{avatarId}/interactions`（见 [获取交互记录](#获取交互记录)）。
- **限制**：当前仅返回会话级摘要（`visitorName` / `messageCount` / `durationSeconds` / `summary` / `createdAt`），**没有逐字对话原文**。导出时如实告知用户；完整逐字记录需后端后续暴露。
- 导出格式：按用户需要整理成 Markdown 或 CSV 交付。

---

## Authentication Boundary

所有分身中心操作都走 SecondMe skill 鉴权：读取 `~/.secondme/credentials` 中的 `accessToken`，请求 `{BASE}/api/secondme/avatar/...`，并带上 `Authorization: Bearer ...`。

Agent 不要直接调用 Java 内部 `/rest/out/avatar/...`，也不要绕过 skill 登录态使用旧的 App 内部接口。

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

### 查看可用官方技能

获取 Avatar 场景下可启用的官方技能和兼容工具。创建分身前，优先调用这个接口让用户选择要启用的能力。

```
GET {BASE}/api/secondme/avatar/skills/available
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| sceneMode | string | 否 | 默认 `avatar_chat` |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/avatar/skills/available?sceneMode=avatar_chat" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

```json
{
  "code": 0,
  "data": {
    "skills": [
      {
        "skillKey": "web",
        "displayName": "Web access",
        "description": "Search the web and fetch web pages when this avatar needs current or external information.",
        "enabled": true
      }
    ]
  }
}
```

使用 `skillKey` 写入创建或更新分身的 `skillKeys`，或写入组合创建接口的 `skills.officialSkillKeys`。

---

### 查看自定义技能列表

获取当前用户已创建的 Avatar 自定义技能。自定义技能可与官方技能一起绑定到分身。

```
GET {BASE}/api/secondme/avatar/custom-skills/list
```

#### 查询参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| sceneMode | string | 否 | 默认 `avatar_chat` |

#### 请求示例

```bash
curl -X GET "{BASE}/api/secondme/avatar/custom-skills/list?sceneMode=avatar_chat" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 响应

```json
{
  "code": 0,
  "data": [
    {
      "id": "9007199254740993",
      "skillKey": "avatar_custom_hiring_faq",
      "title": "Hiring FAQ",
      "description": "Answer hiring process questions.",
      "sceneMode": "avatar_chat",
      "sourceType": "md_text",
      "status": "valid"
    }
  ]
}
```

绑定已有自定义技能时，使用返回的 `skillKey`。

---

### 创建 Markdown 自定义技能

创建 Avatar 自定义技能。当前 skill-facing 流程使用 Markdown 文本上传。

```
POST {BASE}/api/secondme/avatar/custom-skills/create
```

#### 请求参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| title | string | 否 | 技能标题；标准 `SKILL.md` frontmatter 中的 `name` 优先 |
| description | string | 否 | 技能描述；标准 `SKILL.md` frontmatter 中的 `description` 优先 |
| whenToUse | string | 否 | 触发建议 |
| version | string | 否 | 默认 `1.0.0` |
| sceneMode | string | 否 | 默认 `avatar_chat` |
| sceneModes | string[] | 否 | 多场景绑定；通常只传 `["avatar_chat"]` |
| sourceType | string | 是 | 固定传 `md_text` |
| contentMarkdown | string | 是 | Markdown 文本。建议使用标准 `SKILL.md` frontmatter |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/avatar/custom-skills/create" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Local Memory FAQ",
    "description": "Answers from local agent memory.",
    "sceneMode": "avatar_chat",
    "sourceType": "md_text",
    "contentMarkdown": "---\nname: local-memory-faq\ndescription: Answers from local agent memory.\n---\n# Local Memory FAQ\n\n- 用户偏好：直接、具体、先给结论。"
  }'
```

#### 响应

```json
{
  "code": 0,
  "data": {
    "id": "9007199254740993",
    "skillKey": "avatar_custom_local_memory_faq",
    "title": "Local Memory FAQ",
    "description": "Answers from local agent memory.",
    "sceneMode": "avatar_chat",
    "sourceType": "md_text",
    "status": "valid"
  }
}
```

---

### 创建带技能的分身

一次请求内创建 Markdown 自定义技能、绑定官方技能/已有自定义技能，并创建分身。Agent 要帮用户“完整创建一个分身”时优先使用这个接口。

```
POST {BASE}/api/secondme/avatar/skill-create
```

#### 请求参数

该接口包含普通创建分身字段，并新增 `skills`：

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| title | string | 是 | 分身名称 |
| scenarioPrompt | string | 否 | 场景提示词 |
| opening | string | 否 | 开场白 |
| material | object | 否 | 分身材料 |
| modes | object | 否 | 交互模式 |
| distribution | object | 否 | 分发配置 |
| relatedNoteIds | number[] | 否 | 分身专属召回笔记 |
| skills.officialSkillKeys | string[] | 否 | 从可用官方技能接口返回的 `skillKey` |
| skills.existingCustomSkillKeys | string[] | 否 | 从自定义技能列表返回的 `skillKey` |
| skills.customMarkdownSkills | object[] | 否 | 要先创建再绑定的 Markdown 自定义技能 |

`skills.customMarkdownSkills[]` 字段：

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| title | string | 否 | 自定义技能标题 |
| description | string | 否 | 自定义技能描述 |
| whenToUse | string | 否 | 触发建议 |
| version | string | 否 | 默认 `1.0.0` |
| sceneMode | string | 否 | 默认 `avatar_chat` |
| sceneModes | string[] | 否 | 多场景绑定 |
| contentMarkdown | string | 是 | Markdown 文本 |

#### 请求示例

```bash
curl -X POST "{BASE}/api/secondme/avatar/skill-create" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "我的工作分身",
    "scenarioPrompt": "你是基于我的工作习惯、项目背景和本地 agent 记忆创建的分身，回答要直接、具体，并在信息不足时提问。",
    "opening": "你好，我是你的工作分身。你可以问我项目背景、协作偏好或常见决策。",
    "modes": { "textChat": true, "voiceCall": false },
    "distribution": { "apiEnabled": true, "wxappEnabled": false },
    "skills": {
      "officialSkillKeys": ["web"],
      "existingCustomSkillKeys": ["avatar_custom_hiring_faq"],
      "customMarkdownSkills": [
        {
          "title": "Local Agent Memory",
          "description": "Use summarized local agent memory to answer personal workflow questions.",
          "sceneMode": "avatar_chat",
          "contentMarkdown": "---\nname: local-agent-memory\ndescription: Use summarized local agent memory to answer personal workflow questions.\n---\n# Local Agent Memory\n\n## Preferences\n- 回答先给结论，再给必要细节。"
        }
      ]
    }
  }'
```

#### 响应

```json
{
  "code": 0,
  "data": {
    "avatar": {
      "avatarId": 3,
      "type": "custom",
      "title": "我的工作分身",
      "skillKeys": ["web", "avatar_custom_hiring_faq", "avatar_custom_local_agent_memory"],
      "shareCode": "ghi789"
    },
    "createdCustomSkills": [
      {
        "skillKey": "avatar_custom_local_agent_memory",
        "title": "Local Agent Memory",
        "sourceType": "md_text"
      }
    ],
    "enabledSkillKeys": ["web", "avatar_custom_hiring_faq", "avatar_custom_local_agent_memory"]
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
https://second.me/{ownerRoute}/avatar/{shareCode}
```

- `ownerRoute`: 用户的主页路由（从 `GET {BASE}/api/secondme/user/info` 响应的 `route` 字段获取）
- `shareCode`: 分身的分享码（从创建/详情接口返回）

在展示分身信息时，始终拼接并展示完整的分享链接，而不是只展示 shareCode。

---

## Workflow Guidelines

### 创建分身

全新创建分身时，走 [Avatar Studio 旅程](#avatar-studio-旅程)（产品定义 → 收集素材 → 建分身 …），不要直接让用户裸填字段。用户只想快速建一个最小分身时，至少确认 `title`（必填）、`scenarioPrompt`（建议）、`opening`（可选）。

创建成功后，拼接完整分享链接 `https://second.me/{ownerRoute}/avatar/{shareCode}` 并展示给用户。如果当前上下文中没有用户的 `route`，先调用 `GET {BASE}/api/secondme/user/info` 获取。

### 列表展示

- `type: "primary"` 是默认分身（每用户一个，不可删除），在列表中标注
- `type: "custom"` 是自定义分身，可以编辑和删除
- 每个分身都应展示完整分享链接 `https://second.me/{ownerRoute}/avatar/{shareCode}`

### API Key 管理

- 创建后 **立即** 展示 `secretKey` 并提醒用户保存（仅展示一次）
- 发现用量异常时可以 disable 单个 Key，不影响其他 Key
- 删除 API Key 前需要用户确认

### 删除确认

删除分身或 API Key 前，展示即将删除的对象信息并要求用户明确确认。
