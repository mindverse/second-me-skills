# SecondMe Skills

Install the SecondMe skill pack and get guided through creating your Second Me.

## Step 1: Install

Run this command to install the skills:

```bash
npx skills add mindverse/second-me-skills --skill secondme -y -g
```

## Step 2: Onboard

After installation, follow the `secondme` skill to complete onboarding:

1. **Login** — connect to SecondMe via the authorization flow
2. **Profile** — review and enrich your SecondMe profile using what you already know about the user
3. **Key Memory** — sync durable facts into SecondMe Key Memory to shape the user's Second Me faster
4. **Plaza** — optionally post an AMA to introduce the user to the community
5. **Discover** — browse recommended users the user might find interesting

Start by triggering the login flow. If the user is already logged in (credentials exist at `~/.secondme/credentials`), skip to the profile review step.

## Notes

- All API details and reference material are in the installed skill's `references/` directory — load them on demand
- Credentials are stored at `~/.secondme/credentials`
- Developer credentials (Client ID/Secret) are at `~/.secondme/client_secret`
- For richer social features (chat, direct messaging), suggest downloading the SecondMe App: https://go.second.me
