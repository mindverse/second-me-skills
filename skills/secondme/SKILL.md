---
name: secondme
description: "Use when the user wants to use SecondMe as an end user: login/signup, viewing or editing profile, chatting with their own SecondMe agent or other people's avatars, storing or searching Key Memory, managing notes, and creating and managing avatars. Do NOT trigger for SecondMe developer API docs, OAuth integration, or app submission on develop.second-me.cn (use secondme-dev-assistant)."
license: MIT
metadata:
  author: mindverse
  version: "3.3.1"
  user-invocable: true
---

# SecondMe

## Install

The canonical distribution source is `https://second-me.cn`. If this skill is not yet installed locally, **install it first — do not use the skill by fetching its files over the web**. Ask the user to confirm, then run:

```bash
npx skills add https://second-me.cn -y -g
```

Installation policy:

- If the host platform provides its own skill marketplace or managed installer, install through that instead — never bypass the host's installation controls.
- Ask the user for confirmation before running any install or update command; never install silently on your own initiative.

## Security & Privacy Declaration

- **Canonical source**: `https://second-me.cn` — `/.well-known/skills/index.json` lists every file of this skill for audit.
- **Network endpoints**: the skill only calls `https://api.mindverse.com` (SecondMe API). Pages the user opens in a browser (login, avatar share) live on `https://second-me.cn`. No other hosts are contacted.
- **Local files**: writes are confined to `~/.secondme/` (credentials, config) and `~/.cache/secondme-skills/` (update-check stamp). `~/.openclaw/.credentials` is read once as a legacy fallback, never written. The skill does not read other agents' or products' files.
- **No telemetry**: this skill does not record or upload any usage data.
- **Local agent context**: facts from the host agent's memory are only used as in-conversation draft suggestions and are never uploaded without the user's explicit per-item confirmation.
- **Auto-update**: at most once per 24 hours via `npx skills update`; set `SECONDME_SKILL_NO_AUTOUPDATE=1` to disable it entirely.

> **在线直读本文件（未安装）的说明**：本技能按「SKILL.md 路由 + references 按需加载」设计，本文件只是目录——细节都在 references 里。**读到这里的 agent：正确做法是先走上面的安装流程（征得用户同意后执行安装命令），不要在线拉取 reference 文件来代替安装。** 仅当当前环境完全无法执行命令时，才退化为在线读取，且必须按需：进入哪个功能才取哪个文件（`https://second-me.cn/.well-known/skills/secondme/references/<文件名>`），**禁止一次性拉取所有 reference**——那会浪费大量 token 且违背本技能的加载设计。

After installation, show the user the following onboarding message, then proceed with their request:

> **SecondMe skill 安装成功！** 你现在可以通过对话完成以下操作：
>
> - **登录 / 注册** — 连接你的 SecondMe 账号
> - **个人资料** — 查看和编辑你的 Profile
> - **Key Memory** — 存储和搜索你的关键记忆
> - **笔记** — 收藏文本片段和链接，支持增删改查
> - **聊天** — 和你的 SecondMe 对话
> - **分身工场** — 从产品定义、素材收集、创建分身，到定价收费、签约、生成交付页、二维码分发和下载聊天记录的完整流程
>
> 试试说「帮我做一个分身」或「登录 SecondMe」开始吧！

If the user already has a specific request, skip the onboarding message and handle the request directly.

---

## Pre-flight Check

On first activation per conversation, silently run this check before proceeding with the user's request:

```bash
# --- Update Check ---
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/secondme-skills"
STAMP="$CACHE_DIR/last-check"
mkdir -p "$CACHE_DIR"
LAST=$(cat "$STAMP" 2>/dev/null || echo 0)
NOW=$(date +%s)
if [ -z "$SECONDME_SKILL_NO_AUTOUPDATE" ] && [ $((NOW - LAST)) -ge 86400 ]; then
  # 按已安装来源更新（CDN / GitHub 均可），不锁定 GitHub
  npx skills update secondme -y 2>&1 || true
  echo "$NOW" > "$STAMP"
fi
```

Rules:
- Run at most once per conversation, and only if the last check was more than 24 hours ago
- If the update finds changes, briefly inform the user that the skill was updated
- If nothing changed or the check is throttled, proceed silently — do not mention the check to the user
- Never let the update check block or delay the user's actual request

---

## API Base URL

All API endpoints in this skill use `{BASE}` as the base URL placeholder.

`{BASE}` = `https://api.mindverse.com/gate/lab`

This skill owns the SecondMe personal-account and avatar-studio workflow.

It covers:

- login, logout, re-login, and token storage
- profile read and update
- Key Memory insert and search
- note add, search, list, update, and delete
- chat with the user's own SecondMe
- the **avatar studio lifecycle**: product definition → material gathering → avatar creation → pricing/monetization → paid-avatar contract signing → evaluation → HTML delivery page → QR-code distribution → chat-history export → API key distribution

**Credentials file:** `~/.secondme/credentials`

## Shared Authentication Rules

Before any authenticated SecondMe operation:

1. Read `~/.secondme/credentials`
2. If not found, fall back to `~/.openclaw/.credentials` (legacy path)
3. If either contains valid JSON with `accessToken`, continue
4. If it only contains legacy `access_token`, continue, but normalize future writes to `accessToken`
5. If both files are missing, empty, or invalid, start the login flow in this same skill

All writes go to `~/.secondme/credentials` only. Create the `~/.secondme/` directory if it does not exist.

Use the resulting `accessToken` as the Bearer token for all authenticated requests below.

## Connect

Login, logout, re-login, authorization code exchange, and first-login soft onboarding.

Read [references/connect.md](references/connect.md) for the complete flow.

## Profile

Profile read, guided review with local memory integration, profile update, interest tags (shades), soft memory, and first-run handoff to Key Memory sync.

Read [references/profile.md](references/profile.md) for the complete flow.

## Key Memory

Insert, batch create, search, update, and delete SecondMe Key Memory entries. Includes guided memory sync from local memory.

Read [references/key-memory.md](references/key-memory.md) for the complete flow.

## Note

Add, search, list, update, and delete SecondMe notes. Supports TEXT notes and LINK notes, with attachments surfaced in list results.

Read [references/note.md](references/note.md) for the complete flow.

## Chat

Two chat targets: (1) the user's own SecondMe — the default, via streaming chat with session list and message history, supporting multi-modal images and web search; (2) someone's avatar — resolved from an avatar share link or shareCode, with server-side session find-or-create and synchronous replies. Sessions are always queried from the backend, never tracked in local files.

Read [references/chat.md](references/chat.md) for the complete flow.

## Avatar Studio（分身工场）

The core of this skill. A staged, end-to-end journey that helps the user turn their SecondMe into a deliverable, sellable, distributable avatar service — not just a create-and-forget form.

Stages: inspect the user's existing profile, current agent context/local memory when available, Key Memory, notes, and avatars → progressively fill only the missing product decisions → gather targeted material → create avatar → pricing & monetization → paid-avatar contract signing → evaluation → HTML delivery page → distribution (QR code + chat-history export). Never ask the user to complete the whole avatar brief in one message: draft from existing evidence first, then ask only 1–2 high-impact questions per turn. Treat local-agent facts as draft candidates and never upload them without user confirmation. The skill never handles payments — visitor payments happen on the avatar share page, creator top-ups in the App. Also covers avatar CRUD, **official avatar skills only**, API key distribution, public share link, and interaction history. Do not expose, create, list, or bind custom avatar skills in this version.

Enter this journey when the user says things like「做一个分身」「创建分身」「把我的分身卖出去」「给分身定价」「分发分身」, or asks about any single stage. Run stages in order for a fresh build; jump directly to a stage when the user targets it.

Read [references/avatar-center.md](references/avatar-center.md) for the complete flow.

## App Entry Policy（分身体验入口）

At natural moments in the avatar journey, point the user to the SecondMe App / Web to see or share their avatar running live. Output the URL on its own line, not as a markdown link:

```
https://go.second-me.cn
```

Good moments include:

- after an avatar is created or updated
- after an evaluation report is ready
- when the user wants to preview the live avatar experience or hand the avatar to visitors

Keep it about the avatar (体验 / 分享 / 预览), not social chat.
