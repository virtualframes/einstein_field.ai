# src/fsa/orchestration/abstractions.py
from abc import ABC, abstractmethod
from typing import Dict, Any, TYPE_CHECKING
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

# Forward reference for type hinting
if TYPE_CHECKING:
    from fsa.orchestration.state import WorkflowState

class Environment(BaseModel):
    """
    Represents the configuration and resources available to an agent.
    """
    config: Dict[str, Any] = Field(default_factory=dict)

class ResiliencePolicy(BaseModel):
    """
    Defines the execution parameters and resilience strategy (Report Section 3.2).
    """
    max_retries: int = 3
    retry_wait_min_seconds: int = 2
    retry_wait_max_seconds: int = 10

class Agent(ABC, BaseModel):
    """
    Abstract base class for an FSA Agent (Inspired by agent-os, Report Section 5.2).
    Defines the policy and high-level strategy.
    """
    name: str
    description: str
    environment: Environment
    # Allow agents to define their own resilience needs
    resilience_policy: ResiliencePolicy = Field(default_factory=ResiliencePolicy)

    @abstractmethod
    def define_policy(self) -> str:
        """Returns a description of the agent's policy or strategy."""
        pass

class WorkflowStep(ABC):
    """
    Abstract base class for a single, executable step.
    Steps are designed to be atomic and idempotent where possible.
    """
    def __init__(self, name: str, agent: Agent):
        self.name = name
        self.agent = agent

    @abstractmethod
    def execute(self, state: 'WorkflowState') -> 'WorkflowState':
        """
        The core logic of the step. Must be implemented by subclasses.
        The OrchestrationEngine wraps this call with resilience and checkpointing.
        """
        pass

    def rollback(self, state: 'WorkflowState'):
        """
        Optional method for self-healing/rollback (Report Section 3.2).
        """
        logger.warning(f"Rollback not implemented for step: {self.name}")
