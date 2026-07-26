# Parties behavior model

## Official visible model

```text
leader invites character
  -- character joins --> leader + party member state
leader leaves
  -- next invited/member order --> leadership transfer
leader activates Shared Experience
  -- similar levels
  -- all members within 30 fields and one floor
  -- all members actively involved
  --> visible Shared Experience eligibility
```

## Selected current Canary path

```text
Party::create
  --> weak leader + player party association
Party::invitePlayer
  --> inviteList + player invitation
Party::joinParty
  --> remove invite + memberList + status/shared-XP refresh
Party::leaveParty
  --> remove member + leadership transfer or disband
Party::setSharedExperience
  --> leader-only active flag + status evaluation
Party::getMemberSharedExperienceStatus
  --> nonempty + level + 30x30x1 + recent-activity checks
Party::shareExperience
  --> callback-adjusted value + member/leader gain calls
```

## Separate questions

- Party state transitions are distinct from party-chat transport.
- Source-level eligibility checks are distinct from active configuration values.
- Eligibility is distinct from bonus/distribution formula correctness.
- Runtime cleanup is distinct from protocol/client presentation.
- Static source paths do not prove disconnect, death, callback-failure or physical gameplay behavior.
