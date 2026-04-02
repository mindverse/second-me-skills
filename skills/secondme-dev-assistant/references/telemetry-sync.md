# Telemetry Sync

This reference defines the telemetry data sync flow. It uploads pending local analytics events (usage + feedback) to the SecondMe backend.

---

## TOC

- [Prerequisites](#prerequisites)
- [Background Catchup](#background-catchup)
- [Post-Session Sync](#post-session-sync)
- [Sync Implementation](#sync-implementation)
- [Anonymous Mode Stripping](#anonymous-mode-stripping)
- [Error Handling](#error-handling)
- [Rules](#rules)

---

## Prerequisites

Sync requires ALL of the following:
1. `SM_TEL` is `community` or `anonymous` (not `off`)
2. `~/.secondme/credentials` exists with a valid `accessToken`
3. At least one of `usage.jsonl` / `feedback.jsonl` has unsynchronized data (determined by `.sync-offsets`)

If any prerequisite is not met, skip sync silently — do not output anything to the user.

---

## Background Catchup

Execute this section during Pre-flight when `SM_HAS_PENDING_SYNC` is `yes`. Run in the background — do not block the user's request.

Run the [Sync Implementation](#sync-implementation) script. If it fails, ignore the failure silently and continue with the user's request.

---

## Post-Session Sync

Execute this section after Session Telemetry has been logged. This runs in the foreground (the user's workflow is already complete).

Re-check prerequisites (credentials may have been obtained during this session). Then run the [Sync Implementation](#sync-implementation) script.

---

## Sync Implementation

Run the following bash script. Replace no placeholders — all values come from environment variables set during Pre-flight.

```bash
SM_DIR="$HOME/.secondme"
SM_ANALYTICS="$SM_DIR/analytics"
SM_SYNC_OFFSETS="$SM_ANALYTICS/.sync-offsets"
SM_CRED="$SM_DIR/credentials"

python3 << 'SYNC_EOF'
import json, os, sys, time, urllib.request, urllib.error

SM_DIR = os.path.expanduser("~/.secondme")
SM_ANALYTICS = os.path.join(SM_DIR, "analytics")
SM_SYNC_OFFSETS = os.path.join(SM_ANALYTICS, ".sync-offsets")
SM_CRED = os.path.join(SM_DIR, "credentials")
SM_CONFIG = os.path.join(SM_DIR, "config")

# --- Prerequisites ---
if not os.path.isfile(SM_CRED):
    sys.exit(0)

try:
    cred = json.load(open(SM_CRED))
    token = cred.get("accessToken", "")
except Exception:
    sys.exit(0)
if not token:
    sys.exit(0)

try:
    cfg = json.load(open(SM_CONFIG))
    tel_mode = cfg.get("telemetry", "off")
except Exception:
    tel_mode = "off"
if tel_mode == "off":
    sys.exit(0)

# --- Read base URL ---
base_url = cfg.get("baseUrl", "https://app.mindos.com/gate/lab")
ENDPOINT = f"{base_url}/api/secondme/telemetry/events/batch"

# --- Read offsets ---
offsets = {"usage_bytes": 0, "feedback_bytes": 0}
if os.path.isfile(SM_SYNC_OFFSETS):
    try:
        offsets = json.load(open(SM_SYNC_OFFSETS))
    except Exception:
        pass
usage_offset = offsets.get("usage_bytes", 0)
feedback_offset = offsets.get("feedback_bytes", 0)

# --- Read pending events ---
def read_pending(filepath, offset):
    if not os.path.isfile(filepath):
        return [], 0
    file_size = os.path.getsize(filepath)
    if file_size <= offset:
        return [], file_size
    events = []
    with open(filepath, "r") as f:
        f.seek(offset)
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return events, file_size

usage_events, new_usage_offset = read_pending(
    os.path.join(SM_ANALYTICS, "usage.jsonl"), usage_offset
)
feedback_events, new_feedback_offset = read_pending(
    os.path.join(SM_ANALYTICS, "feedback.jsonl"), feedback_offset
)

if not usage_events and not feedback_events:
    sys.exit(0)

# --- Build payload ---
is_anonymous = tel_mode == "anonymous"
device_id = None
if tel_mode == "community":
    did_path = os.path.join(SM_DIR, ".device-id")
    if os.path.isfile(did_path):
        device_id = open(did_path).read().strip() or None

ANONYMOUS_STRIP = {"session", "error_message", "user_intent", "actions_summary",
                   "error_summary", "comment"}

def prepare_event(raw, event_type):
    e = {"type": event_type}
    e["skill"] = raw.get("skill", "secondme-dev-assistant")
    e["ts"] = raw.get("ts", "")
    e["version"] = raw.get("version")
    e["os"] = raw.get("os")
    e["arch"] = raw.get("arch")

    if not is_anonymous:
        e["session"] = raw.get("session")

    if event_type == "usage":
        e["event"] = raw.get("event")
        e["duration_s"] = raw.get("duration_s")
        e["outcome"] = raw.get("outcome")
        e["error_class"] = raw.get("error_class")
        if not is_anonymous:
            e["error_message"] = raw.get("error_message")
            e["user_intent"] = raw.get("user_intent")
        e["phases_used"] = raw.get("phases_used", [])
    elif event_type == "feedback":
        e["outcome"] = raw.get("outcome")
        if not is_anonymous:
            e["actions_summary"] = raw.get("actions_summary")
            e["error_summary"] = raw.get("error_summary")
            e["comment"] = raw.get("comment")
            e["user_intent"] = raw.get("user_intent")
        e["phases_used"] = raw.get("phases_used", [])
        e["references_loaded"] = raw.get("references_loaded", [])
        e["rating"] = raw.get("rating")
        e["issues"] = raw.get("issues", [])

    # Remove None values to keep payload small
    return {k: v for k, v in e.items() if v is not None}

all_events = []
for raw in usage_events:
    all_events.append(prepare_event(raw, "usage"))
for raw in feedback_events:
    all_events.append(prepare_event(raw, "feedback"))

if not all_events:
    sys.exit(0)

# --- Send in batches of 100 ---
BATCH_SIZE = 100
sync_result = "ok"

def send_batch(batch):
    payload = {
        "telemetryMode": tel_mode,
        "events": batch
    }
    if device_id and not is_anonymous:
        payload["deviceId"] = device_id

    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    resp = urllib.request.urlopen(req, timeout=10)
    body = json.loads(resp.read().decode("utf-8"))
    return body

for i in range(0, len(all_events), BATCH_SIZE):
    batch = all_events[i : i + BATCH_SIZE]
    retries = 0
    while retries <= 1:
        try:
            result = send_batch(batch)
            if result.get("code", -1) == 0:
                break
            else:
                sync_result = "server_error"
                break
        except urllib.error.HTTPError as e:
            if e.code == 401:
                sync_result = "auth_failed"
                break
            elif e.code == 429:
                retry_after = int(e.headers.get("Retry-After", "5"))
                time.sleep(min(retry_after, 10))
                retries += 1
            elif e.code in (502, 503, 504):
                time.sleep(2)
                retries += 1
            else:
                sync_result = "server_error"
                break
        except Exception:
            sync_result = "network_error"
            break

    if sync_result != "ok":
        break

# --- Update offsets ---
if sync_result == "ok":
    new_offsets = {
        "usage_bytes": new_usage_offset,
        "feedback_bytes": new_feedback_offset,
    }
else:
    # Keep old offsets on failure
    new_offsets = {
        "usage_bytes": usage_offset,
        "feedback_bytes": feedback_offset,
    }

from datetime import datetime, timezone
new_offsets["last_sync_ts"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
new_offsets["last_sync_result"] = sync_result

os.makedirs(SM_ANALYTICS, exist_ok=True)
json.dump(new_offsets, open(SM_SYNC_OFFSETS, "w"), indent=2)
SYNC_EOF
```

---

## Anonymous Mode Stripping

When `telemetry_mode` is `anonymous`, the sync script removes these fields before sending:

| Removed field | Reason |
|---|---|
| `session` | Cannot correlate sessions |
| `error_message` | May contain semantic information |
| `user_intent` | Free text describing user action |
| `actions_summary` | Free text |
| `error_summary` | Free text |
| `comment` | User feedback text |

Fields preserved for anonymous: `skill`, `ts`, `version`, `os`, `arch`, `outcome`, `duration_s`, `error_class`, `phases_used`, `references_loaded`, `rating`, `issues`.

---

## Error Handling

| Error | Action | Offsets |
|---|---|---|
| 401 Unauthorized | Record `auth_failed`, stop all batches | Not updated |
| 429 Rate Limit | Wait `Retry-After` (max 10s), retry once | Not updated if still fails |
| 502/503/504 | Wait 2s, retry once | Not updated if still fails |
| Network timeout (10s) | Record `network_error` | Not updated |
| Success | Record `ok` | Updated to current file size |
| No credentials | Silent exit | Not updated |
| telemetry=off | Silent exit | N/A |

---

## Rules

- Sync must **never block or delay** user interaction. Background Catchup runs asynchronously; Post-Session Sync runs after the workflow is complete.
- Sync must **never cause visible errors**. All code is wrapped in try/except with silent fallback.
- Local JSONL files are **never modified** by sync — only `.sync-offsets` is updated.
- If credentials are missing, skip sync silently (user not logged in).
- If `telemetry` is `off`, skip sync entirely. Feedback data stays local only.
- The `deviceId` is sent only in `community` mode, never in `anonymous` mode.
- The server also strips anonymous fields as a second safety net.
