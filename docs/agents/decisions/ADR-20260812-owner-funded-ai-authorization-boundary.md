# ADR-20260812: Owner-funded AI authorization boundary

## Status

Accepted by explicit repository-owner instruction on 2026-08-12.

## Context

Agent workflows can discover authenticated Codex/OpenAI sessions, API credentials, connectors, or other paid and quota-limited AI facilities. Technical availability alone does not establish authorization to consume the repository owner's personal quotas, credits, tokens, subscription limits, or metered allowance. Unrequested consumption can exhaust limits needed by the owner for other work.

## Decision

Owner-funded or owner-metered AI resources are deny-by-default for agents.

Agents must not invoke Codex, OpenAI API, paid/limited AI review services, or other mechanisms that consume the owner's personal AI quota, credits, tokens, subscription limits, or metered allowance unless the owner explicitly authorizes that specific use. The same explicit authorization requirement applies to owner-supplied AI/model API keys, access tokens, session tokens, credentials, and secrets.

An available credential, authenticated CLI/browser session, connector, plugin, MCP integration, environment variable, or prior authorization is not standing permission. Authorization is scoped to the current use; a material change of provider, model, scope, or expected consumption requires renewed permission.

When an existing workflow or review policy would normally use an owner-funded AI mechanism without current permission, agents must use a genuinely suitable non-owner-funded alternative when available. If no such mechanism can satisfy a mandatory gate, the task fails closed with an explicit blocker. Agents must not weaken or falsely satisfy validation or review requirements.

## Consequences

- Accidental consumption of the owner's personal Codex/OpenAI or equivalent AI allowance is prohibited by repository governance.
- Mandatory review remains mandatory; lack of permission to consume owner-funded AI creates a blocker when no qualifying alternative exists.
- Repository-local automation that does not consume owner-funded AI resources is unaffected unless another policy restricts it.
- Explicit owner authorization can permit a bounded use without changing this ADR.

## Evaluation

Compliance is evaluated by checking whether an agent invocation would consume an owner-funded or owner-metered AI resource and whether explicit authorization exists for that specific use. Ambiguity fails closed.

## Rollback

The repository owner may supersede or revoke this decision through an explicit governance change. Removing the restriction requires an equally explicit owner decision; availability of credentials or tooling is insufficient.
