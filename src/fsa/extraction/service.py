# src/fsa/extraction/service.py
import openai
import instructor
import logging
from typing import List
# Import the Langfuse-patched OpenAI client for automatic tracing
from langfuse.openai import openai as langfuse_openai

from fsa.core.models import ParsedSection, ClaimExtractionResult, ExtractedClaim, UUID4
from fsa.extraction.prompts import CLAIM_EXTRACTION_SYSTEM_PROMPT, CLAIM_EXTRACTION_USER_TEMPLATE
from fsa.core.observability import get_langfuse_client

logger = logging.getLogger(__name__)

class ClaimExtractionService:
    def __init__(self, model="gpt-4o"):
        self.model = model
        self.langfuse_client = get_langfuse_client()

        # Initialize the Instructor-patched client.
        # We use the Langfuse-patched client as the base for Instructor, combining both capabilities.
        if self.langfuse_client:
            logger.info("Initializing Instructor with Langfuse-patched OpenAI client.")
            self.client = instructor.from_openai(langfuse_openai)
        else:
            # Fallback if Langfuse is not configured
            logger.warning("Initializing Instructor with standard OpenAI client (no tracing).")
            self.client = instructor.from_openai(openai.OpenAI())

    def extract_claims(self, document_id: UUID4, section: ParsedSection) -> List[ExtractedClaim]:
        """Extracts claims from a ParsedSection using an LLM with structured output enforcement."""

        # Define metadata for Langfuse
        trace_name = f"FSA_ClaimExtraction_Doc{str(document_id)[:8]}"
        metadata = {"document_id": str(document_id), "section_id": str(section.section_id), "section_title": section.title}

        user_prompt = CLAIM_EXTRACTION_USER_TEMPLATE.format(
            section_title=section.title,
            section_content=section.content
        )

        messages = [
            {"role": "system", "content": CLAIM_EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        try:
            # Call the LLM, requesting the specific Pydantic model (ClaimExtractionResult).
            # Instructor handles the JSON schema definition, parsing, validation, and retries.
            extracted_result: ClaimExtractionResult = self.client.chat.completions.create(
                model=self.model,
                response_model=ClaimExtractionResult,
                messages=messages,
                temperature=0.0, # Deterministic output
                max_retries=3,   # Instructor provides built-in retries for validation failures
                # Langfuse specific arguments (passed via the patched client if available)
                metadata=metadata,
                tags=["extraction", "fsa_phase1", "instructor"],
                name=trace_name
            )

            logger.info(f"Extracted {len(extracted_result.claims)} claims from section '{section.title}'.")
            return extracted_result.claims

        except Exception as e:
            # Catches OpenAI errors and Instructor validation errors (if retries fail)
            logger.error(f"Error during claim extraction for section {section.section_id}: {e}")
            return []
