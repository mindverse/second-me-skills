# SecondMe OpenClaw Single-Skill Consolidation Design

## Goal

Collapse the seven OpenClaw-facing SecondMe skills into one installable skill without changing the actual user-facing behavior.

## Scope

This consolidation covers these current OpenClaw skills:

- `secondme-connect`
- `secondme-profile`
- `secondme-plaza`
- `secondme-discover`
- `secondme-key-memory`
- `secondme-notes`
- `secondme-activity`

This consolidation does not cover:

- `secondme-external-skill-catalog`
- developer-facing `skills/` workflows

## Chosen Structure

Create a single OpenClaw skill at `openclaw/secondme/SKILL.md`.

Delete the seven legacy OpenClaw skill directories after their content has been merged into the new file.

Keep `openclaw/secondme-external-skill-catalog/SKILL.md` as a separate skill with its own trigger surface and install workflow.

## Behavioral Contract

The new unified skill must preserve the existing behavior from the split skills:

- login, logout, re-login, token exchange, and token persistence
- first successful local-login soft onboarding from profile to Plaza to discover
- profile read/update and draft-before-confirm flow
- Plaza access-gate check before post/detail/comment operations
- invitation redeem and retry guidance for Plaza
- Plaza post publishing and post link construction
- discover browsing with long-timeout guidance and one retry on transient timeout
- Key Memory disambiguation against generic local-memory requests
- Notes creation/search with type-specific payload constraints
- Activity day-overview lookup rules

## Trigger Strategy

The new skill description must cover the combined trigger surface of the seven current skills:

- login and auth requests
- profile and account-info requests
- Plaza, invitation, posting, post detail, and comment requests
- discover / recommended users requests
- explicit Key Memory requests
- notes create/search requests
- activity / day overview requests

At the same time, the new skill must explicitly exclude external-skill-catalog requests so those continue to resolve to `secondme-external-skill-catalog`.

## Internal Organization

The unified skill should stay readable by using one top-level section per capability:

1. shared credential and auth rules
2. connect
3. profile
4. Plaza
5. discover
6. Key Memory
7. notes
8. activity
9. explicit non-scope for external skill catalog

Shared auth text should be written once near the top, while any section-specific constraints remain local to their capability.

## Risks

- A large single skill can become harder to scan, which may reduce execution precision.
- Trigger wording could accidentally absorb requests that should still go to `secondme-external-skill-catalog`.
- Deleting legacy directories can leave stale documentation references behind.

## Mitigation

- Keep sections sharply separated and label them by user intent.
- Add an explicit exclusion note for external skill catalog flows.
- Update README and verify all `openclaw/` references after the consolidation.
