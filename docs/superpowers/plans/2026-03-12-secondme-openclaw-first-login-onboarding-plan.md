# SecondMe OpenClaw First-Login Onboarding Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional first-login onboarding handoff that suggests profile setup, Plaza posting, and discover browsing after the user's first successful SecondMe connection.

**Architecture:** Detect first-time login in the connect skill, then continue the optional guidance through profile and plaza. Each step remains skippable and must give way to the user's direct request.

**Tech Stack:** Markdown skill docs, repo-local skill layout

---

## Chunk 1: Planning Docs

### Task 1: Save design and plan context

**Files:**
- Create: `docs/superpowers/specs/2026-03-12-secondme-openclaw-first-login-onboarding-design.md`
- Create: `docs/superpowers/plans/2026-03-12-secondme-openclaw-first-login-onboarding-plan.md`

- [ ] **Step 1: Write the design document**
- [ ] **Step 2: Write the implementation plan**

## Chunk 2: Connect Skill

### Task 2: Add first-login detection and onboarding prompt

**Files:**
- Modify: `skills/secondme-openclaw-connect/SKILL.md`

- [ ] **Step 1: Record first-time login state during credential check**
- [ ] **Step 2: Add the post-login optional onboarding prompt**
- [ ] **Step 3: Document that the flow stops if the user chooses another path**

## Chunk 3: Profile And Plaza Handoffs

### Task 3: Continue the optional onboarding path

**Files:**
- Modify: `skills/secondme-openclaw-profile/SKILL.md`
- Modify: `skills/secondme-openclaw-plaza/SKILL.md`

- [ ] **Step 1: Add optional Plaza suggestion after first-run profile completion**
- [ ] **Step 2: Add optional discover suggestion after first onboarding-style Plaza step**

## Chunk 4: Verification

### Task 4: Verify optional flow wording

**Files:**
- Modify: `skills/secondme-openclaw-connect/SKILL.md`
- Modify: `skills/secondme-openclaw-profile/SKILL.md`
- Modify: `skills/secondme-openclaw-plaza/SKILL.md`

- [ ] **Step 1: Search for first-login trigger wording**
- [ ] **Step 2: Search for “user can ignore this flow” wording**
- [ ] **Step 3: Confirm no step is described as mandatory**
