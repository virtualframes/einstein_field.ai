# src/fsa/agents/extractor_agent.py
from fsa.orchestration.abstractions import Agent, WorkflowStep, ResiliencePolicy
from fsa.orchestration.state import WorkflowState
from fsa.extraction.service import ClaimExtractionService
import logging

logger = logging.getLogger(__name__)

class ExtractorAgent(Agent):
    name: str = "FSA_Extractor_Agent_v1"
    description: str = "Extracts atomic claims from parsed document sections using structured LLM outputs."
    # LLM calls can be expensive and sometimes flaky; use a standard resilience policy.
    resilience_policy: ResiliencePolicy = ResiliencePolicy(max_retries=3)

    def define_policy(self) -> str:
        return ("Use GPT-4o (zero temperature). Enforce structured Pydantic output via Instructor.")

# --- Steps ---

class ExtractClaimsStep(WorkflowStep):
    def __init__(self, agent: ExtractorAgent):
        super().__init__("Extract_Atomic_Claims", agent)
        # Initialize the service (handles LLM client setup)
        model = agent.environment.config.get("llm_model", "gpt-4o")
        self.service = ClaimExtractionService(model=model)

    def execute(self, state: WorkflowState) -> WorkflowState:
        if not state.sections or not state.document:
            raise RuntimeError("Parsed sections or document ID missing in state. Ensure Parse step completed.")

        # Implementation Note: If this step takes a long time (many sections), it benefits from the Engine's retries.
        # However, if it fails mid-way, it currently restarts from the first section upon retry.
        # Future improvements could include intra-step checkpointing.

        all_claims = []
        logger.info(f"Starting claim extraction across {len(state.sections)} sections.")

        for section in state.sections:
            # Basic filtering
            if len(section.content) < 50 or section.title.lower() in ["references", "acknowledgments", "appendix"]:
                continue

            # This call integrates Langfuse tracing internally via the service implementation (PR 8)
            claims = self.service.extract_claims(state.document.id, section)
            all_claims.extend(claims)

        state.claims = all_claims
        logger.info(f"Total claims extracted: {len(all_claims)}")
        return state
