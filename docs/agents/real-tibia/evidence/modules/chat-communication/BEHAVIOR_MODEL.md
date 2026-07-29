# Chat Communication behavior model

## Selected source flow

```text
configured channel XML
  -- Chat::load -->
normalChannels + optional canJoin/onJoin/onLeave/onSpeak IDs
  -- getChannel/addUser -->
canJoin + onJoin + users map
  -- talkToChannel -->
speak-class normalization + onSpeak + membership-gated talk
  -- removeUser -->
users removal + onLeave
```

Runtime guild and party channels are keyed projections over separate social lifecycles. A premium player may own one private channel; the source allocates an ID, tracks invitations, removes excluded users and closes the channel when deleted or when its owner leaves all channels.

## Separate questions

- Source registration is distinct from configured XML/Lua correctness.
- Membership maps are distinct from party/guild authorization.
- Sending calls are distinct from network delivery and client interpretation.
- Callback presence is distinct from moderation, privacy and security correctness.
- Current Canary source is not physical gameplay or Real Tibia parity proof.
