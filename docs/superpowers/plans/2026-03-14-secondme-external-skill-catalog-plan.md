# SecondMe External Skill Catalog Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the OpenClaw MCP sync skill with a skill that discovers and installs external SecondMe skill bundles.

**Architecture:** Remove the obsolete MCP lifecycle skill and add one focused catalog skill. Keep auth handoff aligned with other OpenClaw skills, and keep installation behavior strictly bound to server-returned `generatedSkillFiles`.

**Tech Stack:** Markdown skill docs, OpenClaw skill conventions, SecondMe third-party agent HTTP APIs

---

## Chunk 1: Replace The Skill Definition

### Task 1: Add the external skill catalog skill

**Files:**
- Create: `openclaw/secondme-external-skill-catalog/SKILL.md`
- Delete: `openclaw/secondme-third-mcp-sync/SKILL.md`

- [ ] **Step 1: Write the failing expectation**

Document that the old skill wrongly targets MCP server sync instead of external skill discovery and installation.

- [ ] **Step 2: Replace the skill definition**

Add frontmatter, auth prerequisite, catalog fetch, detail fetch, installation contract, execution boundary, and output summary for `secondme-external-skill-catalog`.

- [ ] **Step 3: Verify the new skill content**

Run: `sed -n '1,240p' openclaw/secondme-external-skill-catalog/SKILL.md`
Expected: The file references `/skills/available`, `/skills/{skillKey}`, `generatedSkillFiles`, and the no-RPC-during-install rule.

## Chunk 2: Keep Supporting Docs Aligned

### Task 2: Replace the stale design and plan docs

**Files:**
- Create: `docs/superpowers/specs/2026-03-14-secondme-external-skill-catalog-design.md`
- Create: `docs/superpowers/plans/2026-03-14-secondme-external-skill-catalog-plan.md`
- Delete: `docs/superpowers/specs/2026-03-14-secondme-mcp-sync-design.md`
- Delete: `docs/superpowers/plans/2026-03-14-secondme-mcp-sync-plan.md`

- [ ] **Step 1: Write the new design doc**

Capture the new scope, API contract, installation contract, and failure handling.

- [ ] **Step 2: Write the new implementation plan**

Describe the file replacements and verification command.

- [ ] **Step 3: Verify references**

Run: `rg -n "skills/available|skills/\\{skillKey\\}|generatedSkillFiles|mcp/\\{integrationKey\\}/rpc" docs/superpowers/specs/2026-03-14-secondme-external-skill-catalog-design.md docs/superpowers/plans/2026-03-14-secondme-external-skill-catalog-plan.md openclaw/secondme-external-skill-catalog/SKILL.md`
Expected: The new docs and skill all reference the catalog and bundle-install contract.
