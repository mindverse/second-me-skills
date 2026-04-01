# App Bootstrap (Phase 1 & Phase 2)

## Contents

- [Phase 1: Create The SecondMe App And Obtain Credentials](#phase-1-create-the-secondme-app-and-obtain-credentials)
  - [Default Interaction Rule](#default-interaction-rule)
  - [Required Outcome](#required-outcome)
  - [Bootstrap Decision](#bootstrap-decision)
  - [Preferred Input: App Info](#preferred-input-app-info)
  - [Manual Input Fallback](#manual-input-fallback)
  - [Scope-To-Module Inference](#scope-to-module-inference)
- [Phase 2: Client Secret Handling](#phase-2-client-secret-handling)

## Phase 1: Create The SecondMe App And Obtain Credentials

When the user needs a SecondMe app, default to creating it for them through the platform APIs after collecting the required fields and completing authentication.

### Default Interaction Rule

- do not ask the user to manually draft the full App Info block or platform form first
- ask for the minimum missing facts one by one or in a compact list
- then assemble the App Info, create payload, listing payload, or integration payload on the user's behalf
- present the drafted values for confirmation and continue the operation unless the user explicitly wants to fill the form themselves

### Required Outcome

- app exists on the platform
- user has `Client ID`
- user has `Client Secret`
- user knows the redirect URIs and allowed scopes

### Bootstrap Decision

First determine which of these is true:

- user already has complete `App Info`
- user has partial credentials
- user has no app yet

If the user has no app yet:

1. collect the minimum fields needed to create the app
2. authenticate to SecondMe Develop
3. create the app on the user's behalf through the external app create API
4. capture the returned `Client ID` and `Client Secret`
5. save the secret to `~/.secondme/client_secret`
6. explicitly tell the user that the app was created and the secret has already been saved

Only tell the user to go to [develop.second-me.cn](https://develop.second-me.cn) and create it manually when:

- the user explicitly says they want to do it themselves
- required information is still missing and they do not want the assistant to make reasonable defaults
- current auth or platform access prevents the assistant from creating the app directly

### Preferred Input: App Info

Prefer parsing this format:

```text
## App Info
- App Name: my-app
- Client ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
- Client Secret: your-secret-here
- Redirect URIs:
  - http://localhost:3000/api/auth/callback
  - https://my-app.vercel.app/api/auth/callback
- Allowed Scopes: userinfo, chat.read, chat.write, note.write
```

Extract:

- `appName`
- `clientId`
- `clientSecret`
- `redirectUris`
- `allowedScopes`

If both local and production callback URLs are present, prefer the local development callback as the default working callback and keep the full list for future configuration.

### Manual Input Fallback

If App Info is unavailable, collect:

- `App Name`
- `App Description` when available
- `Redirect URIs`
- `Allowed Scopes`

Then create the app on the user's behalf unless they explicitly want to operate manually.

Do not respond by telling the user "please fill these fields yourself" as the default path.

Instead:

- ask the user for any missing facts
- infer safe defaults when the user allows it
- draft the final structure yourself
- ask for confirmation on the drafted result
- then execute the platform action

### Scope-To-Module Inference

Infer the likely app capabilities from scopes:

| Scope | Module |
|------|------|
| `userinfo` | `auth` — user info, interest tags |
| `memory.read` | `memory` — search Key Memory |
| `chat.read` | `chat` — session list, message history |
| `chat.write` | `chat` — stream chat / `act` — stream action |
| `note.write` | `note` — add notes |
| `voice` | `voice` — text-to-speech |
| `plaza.read` | `plaza` — browse feed, post details, comments |
| `plaza.write` | `plaza` — create posts, comments |
| `agent_memory` | `agent_memory` — ingest and query events |

Treat `userinfo` as the baseline scope — almost every app needs it.

## Phase 2: Client Secret Handling

Some actions require the OAuth app `Client Secret`.

Secret file:

- path: `~/.secondme/client_secret`
- directory: `~/.secondme`
- preferred permissions: directory `700`, file `600`

Rules:

1. if the task needs `clientSecret`, first try reading `~/.secondme/client_secret`
2. if the file is missing or empty, ask the user for the secret and save it there
3. after saving, continue using the stored value instead of re-asking
4. never print the raw secret in summaries
5. never invent or silently keep a placeholder

Creation and regeneration rules:

- if this assistant creates an external app and the API returns a new `clientSecret`, save it immediately to `~/.secondme/client_secret`
- if this assistant regenerates the secret and the API returns a new `clientSecret`, replace the file immediately
- after either action, explicitly tell the user that the secret was obtained and already saved to `~/.secondme/client_secret`
- if regeneration happens, also remind the user that the old secret is now invalid

Conflict rule:

- if a different secret already exists and the current task is clearly for another app, warn before overwriting
- if the current flow just created or regenerated the secret for the app being configured, overwrite it and explain what changed

Failure recovery:

- if an API call fails with invalid client, invalid secret, unauthorized client, or another secret-related auth error, treat the stored secret as stale or incorrect
- tell the user the secret in `~/.secondme/client_secret` may be invalid or expired and ask them to replace it
- do not silently keep retrying with the same value
