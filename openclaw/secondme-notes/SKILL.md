---
name: secondme-openclaw-notes
description: Use when the user wants to create or search SecondMe notes in OpenClaw, including text, link, doc, image, or audio note content
user-invocable: true
---

# SecondMe OpenClaw Notes

**Credentials file:** `{baseDir}/.credentials`

## Authentication Prerequisite

Before using this skill, read `{baseDir}/.credentials`.

- If it contains `accessToken`, continue
- If it only contains legacy `access_token`, continue but normalize later
- If the file is missing, empty, or invalid, switch to `secondme-openclaw-connect`

## Create Note

```
POST https://app.mindos.com/gate/in/rest/third-party-agent/v1/notes
Content-Type: application/json
Authorization: Bearer <token>
Body: {
 "title": "<optional>",
 "content": "<optional by type>",
 "memoryType": "TEXT",
 "urls": ["<optional by type>"],
 "audioLanguage": "<optional>",
 "html": "<optional>",
 "permission": "PRIVATE",
 "localId": "<optional>"
}
```

Supported `memoryType` values:
- `TEXT`
- `LINK`
- `DOC`
- `IMAGE`
- `AUDIO`

Field constraints by `memoryType`:
- `TEXT`: `content` is required
- `LINK`: `urls` is required, `content` is optional. Put the real link in `urls`; use `content` only as description text
- `DOC`: `urls` is required
- `IMAGE`: `urls` is required
- `AUDIO`: `urls` is required, `audioLanguage` is optional

Response:
- `data` is the new `noteId`

Text note example:

```json
{
 "title": "Trip Idea",
 "content": "Go to Kyoto in autumn",
 "memoryType": "TEXT",
 "permission": "PRIVATE"
}
```

Link note example:

```json
{
 "title": "Second Me homepage",
 "content": "Official website",
 "memoryType": "LINK",
 "urls": [
 "https://second-me.cn/"
 ],
 "permission": "PRIVATE"
}
```

Image note example:

```json
{
 "title": "Travel photo",
 "memoryType": "IMAGE",
 "urls": [
 "https://cdn.second-me.cn/note/photo-1.jpg"
 ],
 "permission": "PRIVATE"
}
```

Audio note example:

```json
{
 "title": "Voice memo",
 "memoryType": "AUDIO",
 "urls": [
 "https://cdn.second-me.cn/note/audio-1.mp3"
 ],
 "audioLanguage": "en",
 "permission": "PRIVATE"
}
```

## Search Notes

```
GET https://app.mindos.com/gate/in/rest/third-party-agent/v1/notes/search?keyword=<keyword>&pageNo=1&pageSize=20
Authorization: Bearer <token>
```

Common response fields:
- `list`
- `total`

Useful item fields:
- `noteId`
- `title`
- `content`
- `summary`
- `memoryType`
- `createTimestamp`
