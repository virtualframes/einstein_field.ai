# src/fsa/agents/ingestor_agent.py
from fsa.orchestration.abstractions import Agent, WorkflowStep, ResiliencePolicy
from fsa.orchestration.state import WorkflowState
from fsa.ingestion.arxiv_fetcher import ArxivFetcher
from fsa.ingestion.pdf_parser import PDFParser
import logging

logger = logging.getLogger(__name__)

class IngestorAgent(Agent):
    name: str = "FSA_Ingestor_Agent_v1"
    description: str = "Handles fetching and parsing of scientific documents."
    # Define a more robust resilience policy for network operations
    resilience_policy: ResiliencePolicy = ResiliencePolicy(max_retries=5, retry_wait_max_seconds=30)

    def define_policy(self) -> str:
        return "Fetch using robust network retries. Parse PDFs using heuristic section detection (PyMuPDF)."

# --- Steps ---

class FetchArxivStep(WorkflowStep):
    def __init__(self, agent: IngestorAgent):
        super().__init__("Fetch_Arxiv_Document", agent)
        self.fetcher = ArxivFetcher()

    def execute(self, state: WorkflowState) -> WorkflowState:
        arxiv_id = state.context.get("arxiv_id")
        if not arxiv_id:
            raise ValueError("Context must contain 'arxiv_id'.")

        logger.info(f"Fetching ArXiv ID: {arxiv_id}")
        # The ArxivFetcher already uses tenacity internally; the Engine provides outer resilience.
        document, pdf_content = self.fetcher.fetch_by_id(arxiv_id)

        state.document = document
        # Save the artifact robustly using the state manager and store the reference
        state.save_raw_artifact(pdf_content)
        logger.info(f"Successfully fetched document: {document.title}")
        return state

class ParsePDFStep(WorkflowStep):
    def __init__(self, agent: IngestorAgent):
        super().__init__("Parse_PDF_Sections", agent)
        self.parser = PDFParser()
        # Override policy for this specific step if needed (e.g., parsing is less likely to need 5 retries)
        # For now, we rely on the agent's default policy.

    def execute(self, state: WorkflowState) -> WorkflowState:
        if not state.document or not state.raw_artifact_ref:
            raise RuntimeError("Document metadata or artifact reference missing in state. Ensure Fetch step completed.")

        # Load the artifact using the reference managed by the state
        pdf_content = state.load_raw_artifact()

        logger.info(f"Parsing PDF for document ID: {state.document.id}")
        sections = self.parser.parse(state.document, pdf_content)

        state.sections = sections
        return state
