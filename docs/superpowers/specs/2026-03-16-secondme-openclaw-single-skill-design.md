# SecondMe OpenClaw Single-Skill Design

## Goal

Keep exactly one OpenClaw-facing SecondMe skill and align it with the current product boundary.

## Scope

The single skill lives at `openclaw/secondme/SKILL.md` and owns:

- login, logout, re-login, token exchange, and token persistence
- profile read/update with confirmation-first drafting
- Plaza invitation activation plus read-only Plaza access
- discover user browsing
- Key Memory insert and search
- optional guided import of OpenClaw memory facts into SecondMe Key Memory
- activity day-overview lookup
- third-party skill catalog browse, inspect, install, refresh, and re-install

This design does not keep a separate OpenClaw skill for external skill catalog flows.

## Behavioral Changes

### Profile

Profile setup should explicitly focus on:

- `name`
- `aboutMe`
- `originRoute`

`originRoute` must be explained as the SecondMe personal homepage route and described as an alphanumeric identifier.

The profile flow should:

- read the current profile first
- show existing values if present
- ask whether the user wants to update them
- only draft new values when fields are missing or the user asks to change them
- let OpenClaw infer a first draft from known conversation context before asking the user to fill from scratch

### Plaza

OpenClaw should no longer guide or execute Plaza posting.

Plaza scope becomes:

- activation status check
- invitation redeem
- read-only post detail lookup
- read-only comment lookup
- read-only Plaza feed list/search through `/plaza/feed`

When the user asks for posting or richer social actions, the skill should redirect them to the SecondMe App instead of trying to perform the action in OpenClaw.

### Key Memory

Key Memory support returns to the unified skill.

Implemented behaviors:

- explicit source disambiguation from OpenClaw local memory
- direct insert
- batch insert
- extract-mode insert
- update by `memoryId`
- delete by `memoryId`
- search
- optional onboarding suggestion to sync OpenClaw memory into SecondMe after user consent

The consent language should explain that storing memories in SecondMe can help shape the user's SecondMe faster.

### Activity

Activity support returns to the unified skill through day-overview lookup. The user-facing explanation should frame the day overview as covering things like:

- people recommended in discover
- chats involving the user
- the user's Plaza activity

### Third-Party Skills

The unified skill should absorb the existing external skill catalog behavior:

- list installable remote skills
- fetch detail for a chosen `skillKey`
- install server-returned `generatedSkillFiles`
- refresh or re-install a local bundle by fetching the current server version again

Installation rules remain strict:

- use the server-provided bundle exactly as returned
- write every file in `generatedSkillFiles`
- do not synthesize `SKILL.md`, `prompt.md`, or `prompt_short.md`
- do not call downstream RPC execution endpoints during installation

## First-Login Guidance

The first-login onboarding should change from:

- profile
- Plaza posting
- discover

to a path that matches the current capability set:

- profile check and completion
- optional Key Memory sync from OpenClaw memory
- activity or discover exploration

The user must be free to skip or redirect at every step.

## App Reminder Policy

At suitable moments, the skill should remind the user that more social features such as chatting with users or publishing Plaza posts are better experienced in the SecondMe App.

Good reminder moments include:

- after successful login
- when a user asks for posting
- when a user asks for user-to-user chat
- when a read-only OpenClaw flow finishes and a richer social next step would make sense

## Non-Scope

The unified skill should not perform these behaviors:

- Plaza post publishing from OpenClaw
- fabricated Key Memory update/delete API calls
- free-text semantic people search beyond discover browsing
- note creation/search

## Risks

- A single large skill can become harder to scan.
- Multiple read-only and memory-management paths can still be misunderstood if sections are not clearly separated.
- Merging remote skill install behavior into the main skill can blur the line between installation and execution.

## Mitigation

- Keep the document organized by clear user intent sections.
- Keep endpoint sections concrete and label read-only versus write actions clearly.
- Keep a hard execution boundary that installation never calls runtime RPC endpoints.
