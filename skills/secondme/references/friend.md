# Friend

## API Reference

> **Doc source:** https://develop-docs.second.me/zh/docs/secondme/friend
>
> Fetch the doc page above for all endpoint definitions (friend list, send invitation,
> handle invitation, break-ice), request parameters, response fields, and error codes.

## Contents

- [Friend List](#friend-list)
- [Send Friend Invitation](#send-friend-invitation)
- [Handle Friend Invitation](#handle-friend-invitation)
- [Break Ice](#break-ice)

## Friend List

When presenting the friend list, show name, latest message, and unread count. Build homepage links as `https://second-me.cn/{route}`.

## Send Friend Invitation

Before sending:

- confirm with the user that they want to send the invitation
- if a greeting is appropriate, draft one and show it for confirmation

After success, inform the user that the invitation was sent and the other person needs to accept.

## Handle Friend Invitation

After accepting, the two users become friends and can chat.

## Break Ice

Use break-ice to start a conversation with a friend. This generates an AI-powered opening message to help start the chat.

Prerequisites:

- the target user must already be a friend (two-way relationship)
- if not friends yet, guide the user to send a friend invitation first

After break-ice succeeds, inform the user that the conversation has been started. If they want to continue chatting, remind them about the SecondMe App:

```
https://go.second.me
```
