# SecondMe OpenClaw First-Login Onboarding Design

## Goal

Make the first successful SecondMe connection feel guided without turning it into a rigid required flow.

## Trigger

This onboarding should only run when:

- `{baseDir}/.credentials` did not exist, was empty, or was invalid before login
- and the current `auth/token/code` exchange succeeds

It should not run on every re-login.

## Desired Experience

After the first successful connection:

1. Suggest checking or setting up profile information
2. Suggest posting to Plaza
3. Suggest using discover to find interesting people

The flow must stay optional:

- if the user follows, hand off step by step
- if the user says they want something else, stop the onboarding immediately
- do not keep pulling them back to the guided path

## Chosen Structure

### `secondme-openclaw-connect`

Own:

- detect whether this is the first successful local login
- present one short onboarding suggestion after success
- hand off to profile if the user accepts

### `secondme-openclaw-profile`

Own:

- profile read/update
- when the user just completed first-run setup, suggest Plaza as the next optional step

### `secondme-openclaw-plaza`

Own:

- Plaza activation/posting
- after a first onboarding-style Plaza step finishes, suggest discover as the next optional step

### `secondme-openclaw-discover`

No structural change required. It already works as the final suggested step.

## Guardrails

- The onboarding suggestion should be short
- It should mention users can ignore the suggestion and do something else
- It should never block unrelated requests
- It should be easy to skip with one natural user response
