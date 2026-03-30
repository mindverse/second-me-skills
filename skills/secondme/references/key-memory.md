# Key Memory

## API Reference

> **Doc source:** https://develop-docs.second.me/zh/docs/secondme/key-memory
>
> Fetch the doc page above for all endpoint definitions (insert, search, update, delete),
> request parameters, response fields, and error codes.

## Contents

- [Overview](#overview)
- [Guided Memory Sync](#guided-memory-sync)
- [Insert Key Memory](#insert-key-memory)
- [Batch Create Key Memory](#batch-create-key-memory)
- [Search Key Memory](#search-key-memory)
- [Update Key Memory](#update-key-memory)
- [Delete Key Memory](#delete-key-memory)

## Overview

This section is only for explicit SecondMe Key Memory operations.

If the user only says generic `记忆`, `memory`, `你记得吗`, or `查我的记忆`, do not assume they mean this section. That wording may refer to local memory (the assistant's own memory of the user).

If ambiguous, ask:

> 你要查本地记忆，还是 SecondMe 的 Key Memory？

## Guided Memory Sync

If the user is in onboarding, or asks how to shape their SecondMe faster, offer:

> 如果你愿意，我可以把适合长期保存的记忆整理成几条，再分条存进 SecondMe。
>
> 这样通常能更快塑造你的 SecondMe。
>
> 要我先整理一版给你确认吗？

Rules:

- ask for consent before preparing or writing a sync batch
- if the user accepts from the first-login handoff, first review local memory and extract candidate facts that are suitable for long-term storage in SecondMe
- if there are no suitable local memory facts, say so clearly and do not push the import step
- if the user agrees, first show the candidate facts in a compact list
- only write the facts the user confirms
- prefer durable facts such as preferences, stable background, and long-term context
- for this onboarding sync flow, use the batch create endpoint below after the user confirms the list
- after batch create succeeds, report the returned `insertedCount`

## Insert Key Memory

Use Key Memory for durable facts like:

- user preferences
- stable biographical facts
- durable relationship or context facts

## Batch Create Key Memory

Use batch create when the user confirms multiple memory items at once.

There is no dedicated batch endpoint. To insert multiple memories, call the single insert endpoint once per item. Send one request per memory item sequentially. After all requests complete, report how many were inserted successfully.

## Search Key Memory

Do not merge local memory results with SecondMe Key Memory results unless the user explicitly asks for both.

## Update Key Memory

Rules:

- update only after the user confirms which memory to change
- only send the fields the user wants changed

## Delete Key Memory

Rules:

- confirm the deletion target with the user before calling delete
