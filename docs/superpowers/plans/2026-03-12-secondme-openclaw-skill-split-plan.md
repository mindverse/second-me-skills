# SecondMe OpenClaw Skill Split Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the oversized OpenClaw SecondMe skill into a thin router and focused subskills so intent matching is more precise.

**Architecture:** Keep `skills/secondme-openclaw/SKILL.md` as a thin router and move operational rules into dedicated subskills with narrow trigger descriptions. Reuse the same auth/API contract, but isolate it by user intent.

**Tech Stack:** Markdown skill docs, repo-local skill layout

---

## Chunk 1: Planning Docs

### Task 1: Save design and plan context

**Files:**
- Create: `docs/superpowers/specs/2026-03-12-secondme-openclaw-skill-split-design.md`
- Create: `docs/superpowers/plans/2026-03-12-secondme-openclaw-skill-split-plan.md`

- [ ] **Step 1: Write the design document**
- [ ] **Step 2: Write the implementation plan**

## Chunk 2: Router Skill

### Task 2: Replace the large router body

**Files:**
- Modify: `skills/secondme-openclaw/SKILL.md`

- [ ] **Step 1: Rename the frontmatter skill name to `secondme-openclaw`**
- [ ] **Step 2: Remove large operational sections**
- [ ] **Step 3: Replace with a short routing table and ambiguity handling**

## Chunk 3: Focused Skills

### Task 3: Add focused subskills

**Files:**
- Create: `skills/secondme-openclaw-connect/SKILL.md`
- Create: `skills/secondme-openclaw-profile/SKILL.md`
- Create: `skills/secondme-openclaw-plaza/SKILL.md`
- Create: `skills/secondme-openclaw-discover/SKILL.md`
- Create: `skills/secondme-openclaw-key-memory/SKILL.md`
- Create: `skills/secondme-openclaw-notes/SKILL.md`
- Create: `skills/secondme-openclaw-activity/SKILL.md`

- [ ] **Step 1: Write connect skill**
- [ ] **Step 2: Write profile skill**
- [ ] **Step 3: Write Plaza skill**
- [ ] **Step 4: Write discover skill**
- [ ] **Step 5: Write key-memory skill**
- [ ] **Step 6: Write notes skill**
- [ ] **Step 7: Write activity skill**

## Chunk 4: Verification

### Task 4: Verify trigger wording and structure

**Files:**
- Modify: `skills/secondme-openclaw/SKILL.md`
- Modify: `skills/secondme-openclaw-connect/SKILL.md`
- Modify: `skills/secondme-openclaw-profile/SKILL.md`
- Modify: `skills/secondme-openclaw-plaza/SKILL.md`
- Modify: `skills/secondme-openclaw-discover/SKILL.md`
- Modify: `skills/secondme-openclaw-key-memory/SKILL.md`
- Modify: `skills/secondme-openclaw-notes/SKILL.md`
- Modify: `skills/secondme-openclaw-activity/SKILL.md`

- [ ] **Step 1: Run repository searches for skill names and trigger phrases**
- [ ] **Step 2: Confirm the router is short and the focused skills are specific**
- [ ] **Step 3: Confirm no stale "one big skill" wording remains**
