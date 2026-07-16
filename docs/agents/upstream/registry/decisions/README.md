# Reviewed upstream decisions

Store one JSON-compatible YAML file per reviewed candidate.

Example:

```json
{
  "schema_version": 1,
  "candidate_id": "opentibiabr-canary:pull:4034",
  "source_id": "opentibiabr-canary",
  "candidate_revision": "0000000000000000000000000000000000000000",
  "status": "partial-value",
  "reason": "Only the bounded validator correction is relevant to current Canary.",
  "evidence": [
    "Current-main source and focused tests reviewed",
    "Exact upstream PR revision inspected"
  ],
  "modules": ["otbm-tooling"],
  "local_sha": null,
  "decided_at": "2026-07-14T12:00:00Z",
  "decided_by": "reviewer",
  "supersedes": []
}
```

Replace the example values with real evidence. Never copy a report-row conclusion into a decision without reviewing current local behavior.
