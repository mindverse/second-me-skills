# SecondMe OpenClaw Single-Skill Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refine the unified OpenClaw `secondme` skill so it matches the current product boundary: one skill, read-only Plaza, restored Key Memory and activity, and merged third-party skill catalog flows.

**Architecture:** Update the current `openclaw/secondme/SKILL.md` in place, merging the catalog installation rules into the main skill while tightening profile, Plaza, onboarding, and App reminder behavior. Remove the separate `openclaw/secondme-external-skill-catalog` entry so OpenClaw exposes only one skill.

**Tech Stack:** Markdown skill documents, repository README, ripgrep-based verification

---

## Chunk 1: Design And Documentation Alignment

### Task 1: Align the current spec and plan with the approved behavior

**Files:**
- Modify: `docs/superpowers/specs/2026-03-16-secondme-openclaw-single-skill-design.md`
- Modify: `docs/superpowers/plans/2026-03-16-secondme-openclaw-single-skill-plan.md`

- [ ] **Step 1: Rewrite the design doc**

Capture these approved constraints:
- one OpenClaw skill only
- profile focuses on `name`, `aboutMe`, and `originRoute`
- Plaza posting removed from OpenClaw
- Key Memory add/search/update/delete restored, including batch sync
- activity restored
- third-party skill catalog merged into the main skill
- App reminder policy added

- [ ] **Step 2: Rewrite the implementation plan**

Document the file edits, cleanup, and verification commands that implement the revised single-skill behavior.

## Chunk 2: Unified Skill Revision

### Task 2: Update `openclaw/secondme/SKILL.md`

**Files:**
- Modify: `openclaw/secondme/SKILL.md`

- [ ] **Step 1: Tighten the frontmatter and introduction**

Describe the single skill as covering:
- login/auth
- profile
- Plaza read-only access
- discover
- Key Memory
- activity
- third-party skill management

- [ ] **Step 2: Rewrite the onboarding and profile flow**

Require profile-first read, existing-value confirmation, context-based drafting, and an explanation of `originRoute` as an alphanumeric homepage route.

- [ ] **Step 3: Replace Plaza posting with read-only guidance**

Keep activation, invitation redeem, post details, comments, and `/plaza/feed` read-only list/search. Add App fallback messaging for posting requests.

- [ ] **Step 4: Restore Key Memory and activity sections**

Add:
- explicit Key Memory disambiguation
- direct and extract insert
- batch insert for guided sync
- search
- onboarding consent flow for importing OpenClaw memory
- update and delete by `memoryId`
- day overview activity lookup

- [ ] **Step 5: Merge third-party skill catalog behavior**

Add catalog list/detail/install/reinstall rules using:
- `GET /skills/available`
- `GET /skills/{skillKey}`
- strict `generatedSkillFiles` installation behavior
- no RPC calls during install

- [ ] **Step 6: Add App reminder rules**

At suitable moments, direct users to the SecondMe App for richer features such as chatting and posting.

## Chunk 3: Single-Skill Cleanup

### Task 3: Remove the extra OpenClaw skill entry and sync README

**Files:**
- Delete: `openclaw/secondme-external-skill-catalog/SKILL.md`
- Modify: `README.md`

- [ ] **Step 1: Delete the separate external catalog skill**

Only do this after the main `secondme` skill contains the catalog behavior.

- [ ] **Step 2: Update README usage examples**

Advertise only `openclaw/secondme` for OpenClaw users and describe its merged capability set.

- [ ] **Step 3: Update the OpenClaw capability table and tree**

Remove the standalone catalog skill from the README table and project structure.

## Chunk 4: Verification

### Task 4: Run text-level regression checks

**Files:**
- Verify: `openclaw/secondme/SKILL.md`
- Verify: `README.md`

- [ ] **Step 1: Verify required behavior anchors exist**

Run: `rg -n "originRoute|邀请码|third-party-agent/v1/plaza/access|plaza/feed|discover/users|memories/key|memories/key/batch|events/day-overview|skills/available|generatedSkillFiles|SecondMe App" openclaw/secondme/SKILL.md`
Expected: all revised capability anchors are present.

- [ ] **Step 2: Verify OpenClaw exposes one skill**

Run: `find openclaw -maxdepth 2 -name SKILL.md | sort`
Expected: only `openclaw/secondme/SKILL.md`

- [ ] **Step 3: Verify README only advertises the unified skill**

Run: `rg -n "secondme-external-skill-catalog|openclaw/secondme-external-skill-catalog" README.md openclaw`
Expected: no remaining README or runtime references to the deleted separate skill.

- [ ] **Step 4: Inspect final diff**

Run: `git diff -- docs/superpowers/specs/2026-03-16-secondme-openclaw-single-skill-design.md docs/superpowers/plans/2026-03-16-secondme-openclaw-single-skill-plan.md README.md openclaw`
Expected: the main skill is revised, the standalone catalog skill is removed, and docs describe the single-skill model.
