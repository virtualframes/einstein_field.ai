# src/fsa/core/models.py
from pydantic import BaseModel, Field, HttpUrl, UUID4
from enum import Enum
from typing import List, Dict, Optional, Any
import uuid
from datetime import datetime

# --- Enums ---

class DocumentSource(str, Enum):
    ARXIV = "arxiv"
    ZENODO = "zenodo"
    GITHUB = "github"
    RAW_PDF = "raw_pdf"

class ClaimType(str, Enum):
    """Classification of the scientific claim."""
    THEOREM = "THEOREM"       # Mathematical/logical proof
    EMPIRICAL = "EMPIRICAL"   # Based on data/experiment
    PREDICTION = "PREDICTION" # Forecasts a future outcome
    DEFINITION = "DEFINITION" # Defines a new term or concept
    ASSERTION = "ASSERTION"   # Strong statement presented as fact

# --- Core Models (To be persisted later) ---

class Document(BaseModel):
    """Represents an ingested artifact for auditing."""
    id: UUID4 = Field(default_factory=uuid.uuid4)
    source_url: Optional[HttpUrl]
    title: str
    authors: List[str] = Field(default_factory=list)
    source_type: DocumentSource
    raw_content_hash: str # SHA256 hash of the raw ingested content (e.g., PDF bytes)
    ingest_time: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ParsedSection(BaseModel):
    """A structured section of the parsed document."""
    section_id: UUID4 = Field(default_factory=uuid.uuid4)
    document_id: UUID4
    title: str
    content: str
    level: int # e.g., 1 for H1

# --- Extraction Models (Used by Instructor for structured LLM output) ---

class ExtractedClaim(BaseModel):
    """An atomic claim extracted by the LLM."""
    claim_text: str = Field(..., description="The extracted text of the atomic claim.")
    claim_type: ClaimType = Field(..., description="The classification of the claim.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence (0.0-1.0) that this is a substantive, atomic claim.")

class ClaimExtractionResult(BaseModel):
    """The structured response from the claim extraction module."""
    claims: List[ExtractedClaim]
