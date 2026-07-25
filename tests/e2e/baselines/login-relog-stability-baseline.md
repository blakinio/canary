# Login/relog stability baseline execution manifest

This file is evidence-only. It intentionally changes no scenario, runner, workflow, fixture, retry, retention, scheduling, or runtime behavior.

The existing Universal Agent E2E pull-request path filter uses this commit to execute the canonical fallback cell:

- suite: `login`
- scenario: `relog`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`
- datapack: `data-otservbr-global`
- map: `otservbr`
- execution source: pull request #925
- minimum counted attempts: `10`

The exact Canary revision is the commit that introduces this manifest. Every counted attempt and independent cleanup certification must be retained. A later successful retry never replaces an earlier failure.
