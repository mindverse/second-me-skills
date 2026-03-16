# SecondMe OpenClaw Single-Skill Consolidation Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace seven OpenClaw-facing SecondMe skills with one unified `secondme` skill while preserving behavior and keeping `secondme-external-skill-catalog` separate.

**Architecture:** Merge the operational content from the existing split skills into one structured `openclaw/secondme/SKILL.md`. Remove the old directories after the merged skill is complete, then update repository documentation to point at the new single-skill entry.

**Tech Stack:** Markdown skill documents, repository docs, ripgrep-based text verification

---

## Chunk 1: Consolidated Skill Content

### Task 1: Build the unified OpenClaw skill

**Files:**
- Create: `openclaw/secondme/SKILL.md`
- Reference: `openclaw/secondme-connect/SKILL.md`
- Reference: `openclaw/secondme-profile/SKILL.md`
- Reference: `openclaw/secondme-plaza/SKILL.md`
- Reference: `openclaw/secondme-discover/SKILL.md`
- Reference: `openclaw/secondme-key-memory/SKILL.md`
- Reference: `openclaw/secondme-notes/SKILL.md`
- Reference: `openclaw/secondme-activity/SKILL.md`

- [ ] **Step 1: Draft the failing content checklist**

Create a checklist covering these preserved behaviors:
- login/logout/re-login
- first-time onboarding
- profile draft and confirm flow
- Plaza access gate and invitation redeem
- discover timeout handling
- Key Memory disambiguation
- note type constraints
- activity lookup rules
- explicit exclusion of `secondme-external-skill-catalog`

- [ ] **Step 2: Verify the current split skills are the source of truth**

Run: `rg -n "firstTimeLocalConnect|邀请码|discover/users|Key Memory|memoryType|day-overview|skills/available" openclaw/secondme-*/SKILL.md`
Expected: matches in the split skills that anchor every preserved rule

- [ ] **Step 3: Write the unified skill**

Create `openclaw/secondme/SKILL.md` with:
- one combined frontmatter name and description
- one shared credential/auth section
- intent-based sections for connect, profile, Plaza, discover, Key Memory, notes, and activity
- a clear boundary note that external skill catalog requests are out of scope

- [ ] **Step 4: Verify the unified skill contains every required behavior**

Run: `rg -n "firstTimeLocalConnect|邀请码|discover/users|Key Memory|memoryType|day-overview|external-skill-catalog" openclaw/secondme/SKILL.md`
Expected: the merged skill includes all preserved anchors and the external-catalog exclusion

## Chunk 2: Remove Legacy Skill Directories

### Task 2: Delete obsolete split skills

**Files:**
- Delete: `openclaw/secondme-connect/SKILL.md`
- Delete: `openclaw/secondme-profile/SKILL.md`
- Delete: `openclaw/secondme-plaza/SKILL.md`
- Delete: `openclaw/secondme-discover/SKILL.md`
- Delete: `openclaw/secondme-key-memory/SKILL.md`
- Delete: `openclaw/secondme-notes/SKILL.md`
- Delete: `openclaw/secondme-activity/SKILL.md`

- [ ] **Step 1: Delete the seven legacy skill files**

Remove the split skills only after the unified skill exists.

- [ ] **Step 2: Verify only the intended OpenClaw skills remain**

Run: `find openclaw -maxdepth 2 -name SKILL.md | sort`
Expected: `openclaw/secondme/SKILL.md` and `openclaw/secondme-external-skill-catalog/SKILL.md`

## Chunk 3: Documentation Sync

### Task 3: Update README and references

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update installation examples**

Replace the seven split OpenClaw skill names with the unified `openclaw/secondme` entry while keeping `openclaw/secondme-external-skill-catalog`.

- [ ] **Step 2: Update the capability table and project tree**

Describe the unified skill as owning login, profile, Plaza, discover, Key Memory, notes, and activity.

- [ ] **Step 3: Verify README references**

Run: `rg -n "secondme-connect|secondme-profile|secondme-plaza|secondme-discover|secondme-key-memory|secondme-notes|secondme-activity|secondme|secondme-external-skill-catalog" README.md`
Expected: README only advertises `secondme` and `secondme-external-skill-catalog`

## Chunk 4: Regression Verification

### Task 4: Run text-level regression checks

**Files:**
- Verify: `openclaw/secondme/SKILL.md`
- Verify: `openclaw/secondme-external-skill-catalog/SKILL.md`
- Verify: `README.md`

- [ ] **Step 1: Check for stale split-skill references outside docs history**

Run: `rg -n "secondme-connect|secondme-profile|secondme-plaza|secondme-discover|secondme-key-memory|secondme-notes|secondme-activity" openclaw README.md`
Expected: no remaining runtime or README references to deleted split skills

- [ ] **Step 2: Confirm external catalog remains separate**

Run: `rg -n "skills/available|generatedSkillFiles|switch to \`secondme\`" openclaw/secondme/SKILL.md openclaw/secondme-external-skill-catalog/SKILL.md`
Expected: catalog-specific install flow appears only in `secondme-external-skill-catalog`; auth fallback in the catalog skill points to the unified `secondme`

- [ ] **Step 3: Inspect final diff**

Run: `git diff -- docs/superpowers/specs/2026-03-16-secondme-openclaw-single-skill-design.md docs/superpowers/plans/2026-03-16-secondme-openclaw-single-skill-plan.md README.md openclaw`
Expected: one new unified skill, seven deletions, README updates, and no change to catalog installation logic beyond the auth fallback name
