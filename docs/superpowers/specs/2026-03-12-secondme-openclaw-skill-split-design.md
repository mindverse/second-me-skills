# SecondMe OpenClaw Skill Split Design

## Goal

Improve trigger precision for the OpenClaw-facing SecondMe integration by replacing one large, multi-purpose skill with a thin router plus several focused skills.

## Problem

The existing [skills/secondme-openclaw/SKILL.md](/Users/daihaochen/ccccccccc/idea-workspace/Second-Me-Skills/skills/secondme-openclaw/SKILL.md) bundles login, relay config, profile, Plaza, discover, Key Memory, Notes, and day-overview into one document. Its trigger surface is too broad and causes:

- weak skill selection for specific intents
- collisions with OpenClaw local memory when users mention memory-like concepts
- lower quality execution because unrelated rules sit in the same context

## Chosen Approach

Use a thin router plus focused subskills.

### Router skill

Keep [skills/secondme-openclaw/SKILL.md](/Users/daihaochen/ccccccccc/idea-workspace/Second-Me-Skills/skills/secondme-openclaw/SKILL.md), but narrow it to:

- generic "SecondMe in OpenClaw" mentions
- unclear intent routing
- short menu-based clarification

Rename its frontmatter `name` to `secondme-openclaw` so it no longer collides with the project-generation skill named `secondme`.

### Focused subskills

Add these skills:

- `secondme-openclaw-connect`
- `secondme-openclaw-profile`
- `secondme-openclaw-plaza`
- `secondme-openclaw-discover`
- `secondme-openclaw-key-memory`
- `secondme-openclaw-notes`
- `secondme-openclaw-activity`

Each skill gets:

- a narrow description optimized for trigger matching
- only the API and conversation rules relevant to that intent
- a short auth prerequisite pointing back to the connect skill

## Boundaries

### `secondme-openclaw-connect`

Owns:

- login / re-login / logout
- code exchange
- `.credentials`
- relay config binding

### `secondme-openclaw-profile`

Owns:

- profile read/update
- guided profile completion after login

### `secondme-openclaw-plaza`

Owns:

- Plaza activation status
- invitation redeem
- invitation help messaging
- post / details / comments

### `secondme-openclaw-discover`

Owns:

- nearby user discovery

### `secondme-openclaw-key-memory`

Owns:

- explicit SecondMe Key Memory reads/writes
- memory-source disambiguation against OpenClaw local memory

### `secondme-openclaw-notes`

Owns:

- note creation and search
- note type constraints and examples

### `secondme-openclaw-activity`

Owns:

- day-overview queries

## Trigger Strategy

The main accuracy improvement comes from narrowing descriptions:

- the router only handles broad or ambiguous SecondMe mentions
- the focused skills own explicit nouns like `Key Memory`, `Plaza`, `邀请码`, `Note`, `day overview`
- generic `memory` should no longer rely on the large skill; only explicit `Key Memory` / `SecondMe memory` should target the dedicated memory skill

## Risks

- Some shared auth guidance must be repeated across multiple files.
- If the router is still too broad, it may continue to compete with focused skills.

## Mitigation

- Keep the router short and routing-only.
- Keep focused descriptions specific and keyword-rich.
- Avoid repeating unrelated API details across skills.
