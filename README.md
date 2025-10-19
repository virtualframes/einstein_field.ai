einsteinfield.ai — Verified Math, Agentic RAG, and Self‑Debugging Platform

Authoritative repo for a local-first, agentic platform that ingests messy STEM work, extracts canonical claims, verifies math (symbolic + numeric), tracks provenance, and supports 1M+ token context planning, RAG workflows, and autonomous debugging. This README is the operational contract for coding agents, CI, and reviewers.

---

Overview

einsteinfield.ai converts arbitrary user submissions into audit-ready artifacts: normalized claims, SymPy stubs, symbolic derivation traces, numeric fixtures, detector flags, reviewer verdicts, and compressed long-context summaries. The system is modular, reproducible, open-source, and designed for multi-agent collaboration with deterministic CI and provenance-first guarantees.

Core goals:
- Reliable ingestion of messy, multilingual inputs (PDF, OCR, LaTeX, images).
- Symbolic and numeric verification (SymPy, NumPy/SciPy, interval arithmetic).
- RAG-enabled context retrieval and 1M+ token planning via hierarchical compression.
- Agentic orchestration (extractor, verifier, planner, detector, reviewer) with signed provenance events.
- Self-debugging: agents detect, localize, and propose fixes; CI enforces safe remediation.

---

Architecture (high level)

- Frontend: Next.js React UI (Vercel) — submission UI, claim cards, reviewer dashboards.
- API Gateway: FastAPI — submission endpoints, agent RPC hooks, provenance API.
- Agents: containerized Python workers (/agents) — extractor, verifier, planner, detector, reviewer, coder agents.
- Math Backend: SymPy, NumPy/SciPy, mpmath, interval-arithmetic; optional bridges to Lean/Coq.
- Orchestrator: n8n flows + message bus (Redis/Streams) for event routing and retries.
- Provenance Store: JSON-LD claim graph + signed event log + artifact storage (Postgres + GitHub Artifacts / S3).
- CI: GitHub Actions — lint, unit, integration, artifact checkpointing, planner synchronization.
- Local Compute: Docker Compose local stack (3060 Ti GPU used for heavy numeric workloads).

---

Repo layout

- /frontend — Next.js app, Vercel config
- /backend — FastAPI app, DB models, job APIs
- /agents — extractoragent.py, verifieragent.py, planneragent.py, detectoragent.py, reviewer_agent.py, efai-agent CLI
- /infra — docker-compose, n8n flows, redis, postgres, infra helpers
- /schemas — claimschema.json, provenanceschema.json, event_schema.json, tests
- /prompts — curated OpenAI prompt templates and test cases
- /notebooks — SymPy fixtures, reproducible examples
- /ci — GitHub Actions workflows and reusable steps
- /docs — architecture diagrams, agent contracts, onboarding guides

---

Key schemas and contracts

Claim JSON (canonical):
- claim_id: string
- source_text: original span
- canonical_text: normalized statement
- symbols: [{name,type,units}]
- stub_sympy: SymPy-valid expression or code string
- assumptions: [string]
- fixtures: [{name,params,expected}]
- severity: low|medium|high
- provenance_refs: [evidence IDs]

Event schema (agent events):
- eventid, timestamp (ISO8601), actor (agent:id), action ∈ {intent, claim, update, checkpoint, propen, pr_close, merge, verify, detect, review}
- target_files: [paths]
- targetclaimid: optional
- branch, summary, artifact_url, signature

All agent outputs and PRs must reference event_ids and include signed signatures.

---

CI-driven agent lifecycle

Principles:
- Every agent change is tested, traced, and produces provenance artifacts.
- CI simulates submission→extract→verify→detect→review in integration tests.
- Planner checkpoints and compressed context summaries are versioned as CI artifacts.

Primary GitHub Actions:
- lint — black, flake8, isort, eslint, prettier
- unit-tests — agents and schema tests
- integration-tests — spin minimal Docker Compose stack, run end-to-end scripted flows
- build — reproducible Docker images, pinned lockfiles
- deploy — frontend to Vercel, backend artifacts to GitHub Packages if used
- agent-ci-sync — scheduled replay of recent provenance events, update compressed context summaries, store planner checkpoints

CI checks before merge:
- provenance-intent-check: PR includes intent/checkpoint events for touched files
- no-overlap-check: ensures active-claim index has no unresolved overlaps
- checkpoint-validated: checkpoint artifacts exist and signatures validate
- up-to-date-with-main: branch rebased or CI fails with rebase requirement

Planner checkpoints are persisted as artifacts and required on non-trivial PRs.

---

Agent coordination and conflict avoidance

Protocol:
- Agents announce intent before coding: intent event with target_files, branch, ETA, summary.
- Agents repeatedly emit update events (progress %, notes).
- Agents create signed checkpoint artifacts before opening PRs.
- CLI helper efai-agent provides commands: intent, update, checkpoint, pr-open, refresh, pr-close.
- Branch naming: agent/<agent-id>/<short-desc> or feat/<agent-id>/<short>.
- CODEOWNERS enforce required reviewers for directories.
- On overlapping intents, planner triggers negotiation flow (n8n) to split work or schedule exclusive reservations.
- Agents must run efai-agent refresh (git fetch && rebase) before pushing; conflicts require checkpoint + draft PR + planner notification.

CI gates block merges with unresolved overlaps.

---

Long-context (1M+ token) planning and RAG

Strategy:
- Chunk archival traces into semantic blocks (claims, derivations, reviewer labels, artifacts).
- Build hierarchical compressed summaries: chunk -> summary -> meta-summary. Store embeddings and retrieval indexes.
- Planner composes tasks using: immediate claim context + compressed long-term summary + retrieved docs from RAG store.
- RAG store supports retrieval from: provenance DB, repo content, arXiv/Semantic Scholar, curated knowledge bases.
- Planner maintains checkpoints and a retrieval index; CI job agent-ci-sync periodically recomputes compressed summaries and reindexes.
- Agents use retrieval-first prompts with explicit provenance tokens and retrieval evidence embedding identifiers.

Design pattern: treat the 1M+ context as a retrievable, time-versioned knowledge graph rather than a monolithic context window.

---

Self-debugging, bug detection, and autonomous remediation

Detection layers:
- Unit and integration tests (CI).
- Run-time detectors: contradiction, hallucination, provenance-drift, calibration monitor.
- Agent health monitors: liveness, deterministic-run checks, code-signature validations.

Self-debug cycle:
1. Detector flags anomaly (e.g., failing symbolic transform, mismatch between stub and SymPy parse).
2. Verifier agent emits error event with failing-step trace and suggested fixes.
3. Coder agent creates a draft PR with minimal fix, includes checkpoint artifact and test demonstrating regression.
4. Planner assesses risk; if safe, assigns reviewer_agent for rapid human-in-the-loop approval; else scheduler blocks auto-merge.
5. CI runs integration-tests including previously failing fixture; on pass, PR can be merged with required approvals.

Agents must always include failing-case reproducer tests and a provenance trace in remediation PRs.

---

Local bootstrap and developer tasks

Prereqs:
- Python 3.11+, Node 18+, Docker, Docker Compose, GPU drivers (optional).

Bootstrap:
1. git clone https://github.com/virtualframes/einstein_field.ai
2. cp .env.example .env and fill keys: OPENAIAPIKEY, POSTGRESURL, REDISURL, VERCEL_TOKEN (optional)
3. docker compose up --build
4. backend dev:
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
5. frontend dev:
   cd frontend
   pnpm install
   pnpm dev

First run: POST /submit sample inputs and inspect n8n flows and provenance store.

---

Onboarding checklist for new agents (human or AI)

1. Read this README and /docs/agents.md.
2. Run local bootstrap and ensure infra starts.
3. Execute extractor unit tests and compare outputs to schemas/tests expected claims.
4. Make one small, well-scoped PR:
   - Include intent + checkpoint events
   - Add unit tests and a provenance trace
   - Ensure CI passes lint, unit, integration
5. Tag PR with agent:<agent-id> and add @diego for human review for first 3 PRs.

---

Operational governance and safety

- No automatic publishing of high-severity claims without explicit human reviewer approval.
- Signed provenance events required for all agent actions and CI validations.
- Schema migrations require migration scripts and CI migration tests.
- High-severity detectors cause automatic freeze of relevant provenance graph nodes until human review.

---

Tools & CLI

efai-agent (example usage):
- Intent: efai-agent intent --files agents/verifier_agent.py --branch agent/jules/verifier-refactor --eta 45m --summary "Refactor parser"
- Update: efai-agent update --files ... --progress 40% --note "halfway"
- Checkpoint: efai-agent checkpoint --artifact ./checkpoints/verifier-v1.tar.gz
- Open PR: efai-agent pr-open --branch agent/jules/verifier-refactor --title "Verifier parser refactor" --assignees @diego
- Refresh: efai-agent refresh

All CLI commands emit signed events to provenance store and optionally call n8n webhooks.

---

Troubleshooting & debugging guidelines

- When a verifier failure occurs:
  1. Inspect verifier trace in provenance UI for failing-step id.
  2. Run SymPy notebook in /notebooks with same fixtures.
  3. If parse mismatch, update prompt template in /prompts and run extractor regression tests.
  4. Create minimal reproducer test and checkpoint artifact; open a draft PR referencing event IDs.

- When CI integration-tests fail:
  1. Download planner checkpoint artifact and rehydrate local context.
  2. Run failing scenario locally using Docker Compose.
  3. Emit debug event with stacktrace and failing artifacts.

---

Contribution & PR conventions

- Branch: agent/<agent-id>/<short-desc>
- PR body must include: intenteventid, checkpointartifacturl, touchedfiles list, plannercheckpoint_id.
- Tests: include reproducible unit tests & provenance trace.
- Quality: PRs must pass lint, unit, integration, and no-overlap CI checks.
- Codeowners: enforce required reviewer lists per directory.

---

Contact and maintainers

Project lead: Diego Cortes Hernandez  
Repo: https://github.com/virtualframes/einstein_field.ai/tree/main  
Tag review requests with @diego in PR descriptions; include agent:<agent-id> in commits and PR titles.

---

Appendices, diagrams, and deep agent contracts live in /docs. Use the provenance store UI and CI artifacts to audit, replay, and rehydrate planner context for deterministic debugging and long-term reproducibility.
