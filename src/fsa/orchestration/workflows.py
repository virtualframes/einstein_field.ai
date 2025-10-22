# src/fsa/orchestration/workflows.py
from typing import List, Dict, Any
import logging
from fsa.orchestration.abstractions import WorkflowStep, Environment
from fsa.orchestration.state import WorkflowState, StepStatus
from fsa.orchestration.engine import OrchestrationEngine

# Import Agents and Steps
from fsa.agents.ingestor_agent import IngestorAgent, FetchArxivStep, ParsePDFStep
from fsa.agents.extractor_agent import ExtractorAgent, ExtractClaimsStep

# Setup structured logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

def define_arxiv_audit_workflow_v1(env_config: Dict[str, Any]) -> List[WorkflowStep]:
    """Defines the composition of the ArXiv Forensic Audit Workflow V1."""

    # Initialize Environment
    environment = Environment(config=env_config)

    # Initialize Agents (Policies and Environments are attached)
    ingestor = IngestorAgent(environment=environment)
    extractor = ExtractorAgent(environment=environment)

    # Define Workflow Steps (Sequential Orchestration - Report Section 3.1)
    steps = [
        FetchArxivStep(agent=ingestor),
        ParsePDFStep(agent=ingestor),
        ExtractClaimsStep(agent=extractor),
        # Future steps: GroundingAgent, VerificationAgent
    ]
    return steps

def run_arxiv_audit(arxiv_id: str, env_config: Dict[str, Any]):
    """Helper function to initialize and run the ArXiv audit workflow."""

    workflow_name = "ArXiv_Forensic_Audit_V1"

    # 1. Define the workflow
    steps = define_arxiv_audit_workflow_v1(env_config)

    # 2. Initialize the state
    initial_context = {"arxiv_id": arxiv_id}
    state = WorkflowState(workflow_name=workflow_name, context=initial_context)

    # 3. Initialize the engine
    engine = OrchestrationEngine()

    # 4. Run the workflow
    print(f"Starting workflow {workflow_name} (Run ID: {state.run_id})...")
    final_state = engine.run_workflow(steps, state)

    return final_state

# Example usage (for local testing)
if __name__ == '__main__':
    # Requires environment variables (OPENAI_API_KEY, LANGFUSE_KEYS) to be set
    # Requires running within the Nix environment (nix develop)
    import dotenv
    dotenv.load_dotenv()

    # Use a known ArXiv ID for testing (e.g., "Attention Is All You Need")
    test_arxiv_id = "1706.03762"

    # Configuration (e.g., specifying the LLM model)
    config = {"llm_model": "gpt-4o"}

    result_state = run_arxiv_audit(test_arxiv_id, config)

    print("\n--- Workflow Execution Summary ---")
    print(f"Status: {result_state.status}")
    print(f"Run ID: {result_state.run_id}")
    print(f"Checkpoint: ./checkpoints/{result_state.run_id}.json")
    if result_state.document:
        print(f"Document: {result_state.document.title[:100]}...")
    print(f"Claims Extracted: {len(result_state.claims)}")

    if result_state.status == StepStatus.FAILED:
        print("\nLast Error:")
        # Find the last FAILED log entry
        last_error_log = next((log for log in reversed(result_state.execution_history) if log.status == StepStatus.FAILED), None)
        if last_error_log:
            print(f"Step: {last_error_log.step_name} | Attempt: {last_error_log.attempt} | Message: {last_error_log.message}")

    if result_state.claims:
        print("\nTop 5 Claims Extracted:")
        for claim in result_state.claims[:5]:
            print(f"- [{claim.claim_type}] {claim.claim_text} (Conf: {claim.confidence:.2f})")
