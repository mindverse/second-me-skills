# Post-Session Feedback

This reference defines the post-session feedback flow. Execute **every time** the skill workflow completes, before logging session telemetry.

The flow has two modes:
- **Error / abort sessions** → capture context + ask user for feedback (Part A → B → C → D)
- **Successful sessions** → capture context silently, no questions asked (Part A → D)

---

## TOC

- [Part A: Session Context Capture](#part-a-session-context-capture)
- [Trigger Check](#trigger-check)
- [Part B: User Feedback (error/abort only)](#part-b-user-feedback-errorabort-only)
- [Part C: Issue Details Follow-up](#part-c-issue-details-follow-up)
- [Part D: Write to Local Storage](#part-d-write-to-local-storage)
- [Rules](#rules)

---

## Part A: Session Context Capture

Before anything else, internally summarize the current session. Do not output these to the user — they are metadata for the feedback record.

| Field | How to fill | Example |
|---|---|---|
| `user_intent` | One-sentence summary of what the user wanted. **Must not** contain credentials, tokens, passwords, or PII. | `"创建 SecondMe OAuth 应用并获取凭据"` |
| `actions_summary` | Brief list of key operations performed. Keep under 200 characters. | `"创建了应用、配置 OAuth scopes、保存 Client Secret"` |
| `phases_used` | Which phases from the Trigger Map were activated (e.g., `app_bootstrap`, `requirements`, `implementation_guidance`, `open_apis`, `control_plane_app`, `control_plane_integration`, `maintenance`). | `["app_bootstrap", "implementation_guidance"]` |
| `references_loaded` | Which reference files were read during this session. | `["app-bootstrap.md", "implementation-guidance.md"]` |
| `outcome` | Overall result: `success`, `error`, `partial`, or `abort`. | `"success"` |
| `error_summary` | If outcome is not `success`, describe the error in ≤100 characters. Otherwise `null`. | `"Integration manifest 校验失败：缺少 required scope"` |

---

## Trigger Check

Decide whether to ask the user for feedback:

| `outcome` value | Action |
|---|---|
| `error` or `abort` | → Proceed to [Part B](#part-b-user-feedback-errorabort-only) |
| `success` or `partial` | → Skip Part B & C, jump directly to [Part D](#part-d-write-to-local-storage) with `rating: "auto_skipped"`, `issues: []`, `comment: null` |

---

## Part B: User Feedback (error/abort only)

Use AskUserQuestion to ask:

> 这次操作没有顺利完成，方便说一下遇到了什么问题吗？

Options:

- A) 操作流程复杂或不清晰
- B) 结果不准确或不完整
- C) 缺少需要的功能
- D) 跳过，不想反馈

Map the answer:

| Answer | `rating` | `issues` |
|---|---|---|
| A | `"negative"` | `["complex_flow"]` |
| B | `"negative"` | `["inaccurate_result"]` |
| C | `"negative"` | `["missing_feature"]` |
| D | `"skipped"` | `[]` |

If the user selects D (skip), jump directly to [Part D](#part-d-write-to-local-storage) with `comment: null`.

If the user provides free text via "Other", set `rating: "negative"`, `issues: ["other"]`, and store the text in `comment`.

---

## Part C: Issue Details Follow-up

Only execute if the user selected A, B, or C in Part B.

Use AskUserQuestion:

> 能简单描述一下具体情况吗？（选"跳过"也没关系）

Options:

- A) 跳过
- B) 我来说明

If the user selects B or provides free text via "Other", store the text in `comment`. Otherwise `comment` is `null`.

---

## Part D: Write to Local Storage

Write a single JSON line to `~/.secondme/analytics/feedback.jsonl`.

This runs regardless of the user's telemetry setting — it records session context locally that is always valuable. However, only `community` and `anonymous` mode data will be synced to the server; `off` mode data stays local only.

```bash
SM_DIR="$HOME/.secondme"
SM_ANALYTICS="$SM_DIR/analytics"
mkdir -p "$SM_ANALYTICS"
python3 -c "
import json
e={
  'event': 'feedback',
  'skill': '${SM_SKILL:-secondme-dev-assistant}',
  'ts': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
  'session': '${SM_SESSION_ID:-unknown}',
  'version': '${SM_VERSION:-unknown}',
  'user_intent': USER_INTENT,
  'actions_summary': ACTIONS_SUMMARY,
  'phases_used': PHASES_USED,
  'references_loaded': REFERENCES_LOADED,
  'outcome': OUTCOME,
  'error_summary': ERROR_SUMMARY,
  'rating': RATING,
  'issues': ISSUES,
  'comment': COMMENT
}
print(json.dumps(e, ensure_ascii=False))
" >> "\$SM_ANALYTICS/feedback.jsonl" 2>/dev/null || true
```

Replace the ALL-CAPS placeholders with actual values from Part A–C. String values must be quoted Python strings (e.g., `'negative'`). `null` values should be Python `None`. List values should be Python lists (e.g., `['complex_flow']`).

---

## Rules

- **Part A always runs** — session context is recorded for every session regardless of outcome.
- **Part B & C only run when outcome is `error` or `abort`** — do not ask feedback on successful sessions.
- `feedback.jsonl` is separate from `usage.jsonl`. They share the `session` field for correlation.
- For successful sessions, the record has `rating: "auto_skipped"` — this distinguishes from user-initiated skips.
- Never include credentials, tokens, secrets, or raw API responses in any field.
- When telemetry is `community` or `anonymous`, feedback records will be synced to the SecondMe backend along with usage data. The sync happens after session telemetry is logged.
