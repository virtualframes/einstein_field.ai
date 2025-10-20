PLAN.md — Agent: Jules

Intent
Implement feature X with reproducible logic and CI traceability.

Tasks
- [ ] Scaffold TypeScript interfaces for API response
- [ ] Validate schema against OpenAPI spec
- [ ] Write unit tests for edge cases
- [ ] Submit plan for review to @reviewer-agent

Dependencies
- openapi.yaml
- user.schema.ts
- agents/claude/PLAN.md

Notes
- This plan is canonical and must be updated before execution.
- Jules must revise and optimize this file before any commit.
- Planning Mode is allowed only for scoped subtasks.

CI Governance: SHA Pinning Enforcement

Jules enforces full SHA pinning across all workflows using:

- GitHub Actions policy enforcement (Settings > Actions > Require SHA pinning)
- CI validator workflow (validate-sha.yml) using action-sha-pinned-actions
- Dependabot for weekly SHA updates
- Immutable release pinning for trusted actions

All agents must inherit this policy. Violations trigger CI failure.
