# src/fsa/orchestration/state.py
from pydantic import BaseModel, Field, UUID4
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from enum import Enum
from fsa.core.models import Document, ParsedSection, ExtractedClaim
import logging
import json
import os
import hashlib

logger = logging.getLogger(__name__)

class StepStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ExecutionLog(BaseModel):
    """Provenance log for a single execution attempt (Report Section 7.2)."""
    step_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: StepStatus
    message: Optional[str] = None
    attempt: int # Crucial for tracking retries

class WorkflowState(BaseModel):
    """
    The durable state of a workflow run (Report Section 8).
    """
    run_id: UUID4 = Field(default_factory=uuid.uuid4)
    workflow_name: str

    context: Dict[str, Any] = Field(default_factory=dict)

    # Artifacts
    document: Optional[Document] = None
    # Reference to the raw artifact stored on disk (to keep checkpoint JSON small)
    raw_artifact_ref: Optional[str] = None
    sections: List[ParsedSection] = Field(default_factory=list)
    claims: List[ExtractedClaim] = Field(default_factory=list)

    # History and Status
    execution_history: List[ExecutionLog] = Field(default_factory=list)
    current_step: Optional[str] = None
    status: StepStatus = StepStatus.PENDING

    def add_log(self, step_name: str, status: StepStatus, attempt: int, message: Optional[str] = None):
        self.execution_history.append(ExecutionLog(step_name=step_name, status=status, attempt=attempt, message=message))

    # --- Artifact Management ---

    def _get_artifact_path(self, artifact_dir: str, ref: str) -> str:
        # Organize artifacts by run_id for cleaner management
        run_dir = os.path.join(artifact_dir, str(self.run_id))
        os.makedirs(run_dir, exist_ok=True)
        return os.path.join(run_dir, ref)

    def save_raw_artifact(self, content: bytes, artifact_dir: str = "./artifacts"):
        """Saves large binary artifacts separately and stores a reference."""
        # Use a hash as the reference name
        ref = f"raw_{hashlib.sha256(content).hexdigest()[:16]}.bin"
        path = self._get_artifact_path(artifact_dir, ref)

        # Idempotent write
        if not os.path.exists(path):
            with open(path, 'wb') as f:
                f.write(content)

        self.raw_artifact_ref = ref
        logger.info(f"Saved raw artifact with ref {ref}")

    def load_raw_artifact(self, artifact_dir: str = "./artifacts") -> bytes:
        """Loads the large binary artifact using the stored reference."""
        if not self.raw_artifact_ref:
            raise FileNotFoundError("No raw artifact reference found in state.")

        path = self._get_artifact_path(artifact_dir, self.raw_artifact_ref)
        try:
            with open(path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to load raw artifact {self.raw_artifact_ref}: {e}")
            raise

    # --- Checkpointing Methods (Report Section 8.1) ---

    def checkpoint(self, checkpoint_dir: str = "./checkpoints"):
        """Saves the current state (excluding large artifacts) to a checkpoint file."""
        os.makedirs(checkpoint_dir, exist_ok=True)
        checkpoint_path = os.path.join(checkpoint_dir, f"{self.run_id}.json")

        try:
            with open(checkpoint_path, 'w') as f:
                # Pydantic V2 serialization
                f.write(self.model_dump_json(indent=2))
            logger.info(f"Checkpoint saved successfully for run {self.run_id}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint for run {self.run_id}: {e}")

    @classmethod
    def load_checkpoint(cls, run_id: UUID4, checkpoint_dir: str = "./checkpoints") -> 'WorkflowState':
        """Loads a workflow state from a checkpoint file."""
        checkpoint_path = os.path.join(checkpoint_dir, f"{run_id}.json")
        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(f"Checkpoint file not found for run {run_id}")

        try:
            with open(checkpoint_path, 'r') as f:
                data = json.load(f)
                # Pydantic V2 validation and deserialization
                state = cls.model_validate(data)
            logger.info(f"Checkpoint loaded successfully for run {run_id}")
            return state
        except Exception as e:
            logger.error(f"Failed to load checkpoint for run {run_id}: {e}")
            raise
