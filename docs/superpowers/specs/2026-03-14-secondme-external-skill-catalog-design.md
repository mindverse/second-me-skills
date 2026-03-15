# SecondMe External Skill Catalog Design

## Goal

Replace the OpenClaw MCP sync skill with a focused skill that discovers and installs external SecondMe skill bundles.

## Scope

The new skill owns:

- listing installable external skills from `GET /skills/available`
- showing detail for a selected `skillKey` from `GET /skills/{skillKey}`
- installing the returned `generatedSkillFiles` bundle into the local OpenClaw skill root

It explicitly does not own:

- MCP execution
- third-party business workflows
- calling `POST /mcp/{integrationKey}/rpc` during installation

## Key API Contract

### Catalog endpoint

`GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/skills/available`

Use the authenticated `sm-*` token from `{baseDir}/.credentials`. The response is the source of truth for installable skills and should surface at least `skillKey`, `integrationKey`, `displayName`, `description`, `version`, `actions`, and `toolAllow`.

### Detail endpoint

`GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/skills/{skillKey}`

The detail response must include `generatedSkillFiles`. Installation writes the bundle exactly as returned. No local file content should be synthesized.

## Installation Contract

- local directory name must equal `skillKey`
- file contents must preserve the server payload exactly
- required bundle members currently include `SKILL.md`, `prompt.md`, and `prompt_short.md`
- future bundle files should also be written without special-casing

## Failure Handling

- missing or invalid credentials route to `secondme-openclaw-connect`
- catalog fetch failure stops discovery
- missing `generatedSkillFiles` stops installation
- the skill reports incomplete server payloads instead of generating replacement files

## Output

The user-facing result should say what was discovered, which skill was selected, whether detail fetch succeeded, which files were installed, and whether installation completed.
