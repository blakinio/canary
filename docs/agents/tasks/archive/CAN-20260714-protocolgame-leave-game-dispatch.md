---
task_id: CAN-20260714-protocolgame-leave-game-dispatch
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: OTS-20260714-protocolgame-leave-game-dispatch
status: merged
agent: GPT-5.6-Thinking
branch: fix/protocolgame-leave-game-dispatch
base_branch: main
created: 2026-07-14T20:30:00+02:00
updated: 2026-07-15T12:20:00+02:00
last_verified_commit: "f8deb9fa07488058f6c59ee666e87d9c7f1356a7"
risk: high
related_issue: ""
related_pr: "blakinio/canary#360"
depends_on:
  - CAN-20260713-universal-agent-e2e-platform
blocks:
  - CAN-20260715-current-game-first-frame-framing
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260714-protocolgame-leave-game-dispatch.md
  shared: []
  read_only: []
modules_touched:
  - Connection receive callback lifecycle
  - Protocol dispatcher ownership
  - ProtocolGame leave-game cleanup
  - Current game transport diagnostics
reuses:
  - ProtocolReleaseGate merged in #339
  - exact shared_ptr identity checks
  - existing dispatcher test seam
public_interfaces:
  - none
cross_repo_tasks: []
---

# Goal

Make an already-received `ClientLeaveGame` packet execute exactly once and complete the exact `ProtocolGame -> Player -> Connection` cleanup before stale session work can affect a replacement session for the same character.

# Result

PR #360 was squash-merged as `f8deb9fa07488058f6c59ee666e87d9c7f1356a7` after full implementation-head CI passed on Linux debug/tests, Linux release with Canary and Global smoke, Windows CMake, Windows Solution, macOS and Docker.

The merged change:

- added typed inbound transport rejection diagnostics without advancing accepted client sequence on rejected frames;
- added explicit leave-game lifecycle states and exact session identity checks;
- ensured accepted `ClientLeaveGame` work is pinned through dispatcher completion;
- prevented stale session A release/logout work from detaching or removing active session B;
- added deterministic no-sleep coverage for accepted, duplicate, denied, rejected and stale-session paths.

# Post-merge physical evidence

The unchanged one-process Universal Agent E2E run #35 (`29398519891`) on PR #245 proved that PR #360's leave-game lifecycle was not reached in production because modern client game packets were rejected earlier in inbound framing.

Evidence from `result.json`, server logs and `game-port-7172.pcap`:

- OTClient revision remained pinned to `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`;
- session A reached `login_1=success`, `online_stable_1=confirmed`, `logout_request_1=safe`, `logout_1=complete` and transport close;
- Canary did not persist/remove session A until the ping timeout roughly 53 seconds later;
- session B reached `login_2=success` and then disconnected before `online_stable_2`;
- all post-login client game packets were rejected as sequence mismatches before leave-game dispatch;
- the retained PCAP shows monotonic wire sequences `1,2,3` for session A and `1,2,3,4` for session B.

The independent blocker is therefore a modern first-game-frame body-length/framing defect, not OTClient timing and not the leave-game lifecycle implementation. Follow-up task: `CAN-20260715-current-game-first-frame-framing`.

# Do not repeat

- Do not modify OTClient for this blocker.
- Do not add relog delays, retries, timers, packet-validation relaxation or a two-process workaround.
- Do not treat delayed ping-timeout persistence as successful safe logout.
- Do not infer protocol frame boundaries from TCP segment boundaries.
