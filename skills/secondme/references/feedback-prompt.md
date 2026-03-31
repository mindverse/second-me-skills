# Feedback Preference Flow

This reference defines the first-time feedback/telemetry prompt. Only execute this flow when `TEL_PROMPTED` is `no`.

## Step 1: Ask About Community Mode

Use AskUserQuestion:

> SecondMe Skills 希望变得更好！开启 Community 模式后，会在本地记录匿名使用数据（使用了哪些 skill、使用时长、是否出错），并附带一个稳定的设备 ID 以便追踪趋势和修复问题。此外，每次 skill 使用结束后会询问简短的体验反馈（满意度和改进建议），也仅保存在本地。
>
> 我们**不会**收集任何代码、文件路径、凭据或个人信息。
> 你可以随时编辑 `~/.secondme/config` 中的 `telemetry` 字段来更改设置。

Options:

- A) 好的，帮助 SecondMe 改进！（推荐）
- B) 不了，谢谢

## Step 2: Handle Response

### If A (community)

Run:

```bash
SM_DIR="$HOME/.secondme"
SM_CONFIG="$SM_DIR/config"
mkdir -p "$SM_DIR"
python3 -c "
import json, os
p = os.path.expanduser('$SM_CONFIG')
try: d = json.load(open(p))
except: d = {}
d['telemetry'] = 'community'
json.dump(d, open(p, 'w'), indent=2)
"
touch "$SM_DIR/.feedback-prompted"
```

Then generate a stable device ID:

```bash
SM_DIR="$HOME/.secondme"
if [ ! -f "$SM_DIR/.device-id" ]; then
  python3 -c "import uuid; print(uuid.uuid4().hex)" > "$SM_DIR/.device-id"
fi
```

Proceed with the user's original request.

### If B (declined community)

Ask a follow-up question using AskUserQuestion:

> 那 Anonymous 模式呢？我们只会在本地记录"有人使用了某个 skill"——没有设备 ID，无法关联会话，只是一个计数器。

Options:

- A) 可以，匿名模式没问题
- B) 不了，完全关闭

#### If B → A (anonymous)

Run:

```bash
SM_DIR="$HOME/.secondme"
SM_CONFIG="$SM_DIR/config"
mkdir -p "$SM_DIR"
python3 -c "
import json, os
p = os.path.expanduser('$SM_CONFIG')
try: d = json.load(open(p))
except: d = {}
d['telemetry'] = 'anonymous'
json.dump(d, open(p, 'w'), indent=2)
"
touch "$SM_DIR/.feedback-prompted"
```

Proceed with the user's original request.

#### If B → B (fully off)

Run:

```bash
SM_DIR="$HOME/.secondme"
SM_CONFIG="$SM_DIR/config"
mkdir -p "$SM_DIR"
python3 -c "
import json, os
p = os.path.expanduser('$SM_CONFIG')
try: d = json.load(open(p))
except: d = {}
d['telemetry'] = 'off'
json.dump(d, open(p, 'w'), indent=2)
"
touch "$SM_DIR/.feedback-prompted"
```

Proceed with the user's original request.

## Rules

- This flow runs **only once**. The `touch ~/.secondme/.feedback-prompted` marker ensures it never repeats.
- If `TEL_PROMPTED` is already `yes`, skip this entire flow.
- The config write uses `python3 -c` to safely merge into the existing JSON config without overwriting other keys (like `baseUrl`).
- After the prompt is handled, **immediately continue** with the user's actual request. Do not add extra commentary about the choice.
