# Feedback Preference Flow

This reference defines the first-time feedback/telemetry prompt. Only execute this flow when `TEL_PROMPTED` is `no`.

## Step 1: Ask Once, Neutrally

Telemetry is **off by default**. Ask exactly one question with the three modes presented neutrally — do not mark any option as recommended, and do not re-ask if the user declines.

Use AskUserQuestion:

> SecondMe Skills 可以记录匿名使用数据来帮助改进产品。你可以选择：
>
> - **Community**：记录使用了哪些 skill、使用时长、是否出错，附带一个随机生成的设备 ID 以便追踪趋势；使用结束后记录简短体验反馈。
> - **Anonymous**：只记录“有人使用了某个 skill”的计数，无设备 ID，无法关联会话。
> - **Off**：完全不记录。
>
> 前两种模式下数据保存在本地 `~/.secondme/analytics/`，登录后同步到 SecondMe 服务端。我们**不会**收集任何代码、文件路径、凭据或个人信息。之后可随时编辑 `~/.secondme/config` 中的 `telemetry` 字段更改设置。

Options:

- A) Community 模式
- B) Anonymous 模式
- C) 完全关闭

## Step 2: Persist the Choice

Write the selected mode (`community` / `anonymous` / `off`) and mark the prompt as done:

```bash
SM_DIR="$HOME/.secondme"
SM_CONFIG="$SM_DIR/config"
SM_MODE="<community|anonymous|off>"
mkdir -p "$SM_DIR"
python3 -c "
import json, os
p = os.path.expanduser('$SM_CONFIG')
try: d = json.load(open(p))
except: d = {}
d['telemetry'] = '$SM_MODE'
json.dump(d, open(p, 'w'), indent=2)
"
touch "$SM_DIR/.feedback-prompted"
```

If the user chose Community, also generate a stable device ID:

```bash
SM_DIR="$HOME/.secondme"
if [ ! -f "$SM_DIR/.device-id" ]; then
  python3 -c "import uuid; print(uuid.uuid4().hex)" > "$SM_DIR/.device-id"
fi
```

Proceed with the user's original request.

## Rules

- This flow runs **only once**. The `touch ~/.secondme/.feedback-prompted` marker ensures it never repeats.
- If `TEL_PROMPTED` is already `yes`, skip this entire flow.
- Ask exactly one question. Never re-ask, upsell, or follow up after the user picks a mode — including when they pick Off.
- The config write uses `python3 -c` to safely merge into the existing JSON config without overwriting other keys (like `baseUrl`).
- After the prompt is handled, **immediately continue** with the user's actual request. Do not add extra commentary about the choice.
