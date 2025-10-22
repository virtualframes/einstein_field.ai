# src/fsa/orchestration/engine.py
from typing import List, Optional
import logging
from tenacity import Retrying, stop_after_attempt, wait_exponential, RetryError

from fsa.orchestration.abstractions import WorkflowStep, ResiliencePolicy
from fsa.orchestration.state import WorkflowState, StepStatus
from fsa.core.observability import get_langfuse_client
from langfuse.client import StatefulTraceClient

logger = logging.getLogger(__name__)

class OrchestrationEngine:
    """
    Manages the execution of workflows, handling sequencing, state, resilience, and observability.
    """
    def __init__(self, checkpoint_dir: str = "./checkpoints", artifact_dir: str = "./artifacts"):
        self.checkpoint_dir = checkpoint_dir
        self.artifact_dir = artifact_dir
        self.langfuse_client = get_langfuse_client()

    def run_workflow(self, steps: List[WorkflowStep], initial_state: WorkflowState):
        """Executes the workflow steps sequentially."""
        state = initial_state
        # Ensure status is RUNNING if starting or resuming
        if state.status != StepStatus.COMPLETED and state.status != StepStatus.FAILED:
             state.status = StepStatus.RUNNING

        # Initialize Langfuse Trace (Report Section 7.1)
        trace = self._initialize_trace(state)
        logger.info(f"Starting/Resuming workflow '{state.workflow_name}' (Run ID: {state.run_id})")

        # Determine starting step (for resumption, Report Section 8.1)
        start_index = self._get_start_index(steps, state)

        for i in range(start_index, len(steps)):
            step = steps[i]
            state.current_step = step.name

            logger.info(f"--- Executing step {i+1}/{len(steps)}: {step.name} ---")

            # Initialize Langfuse Span for the step
            span = self._initialize_span(trace, step, state)

            try:
                # Execute the step with resilience (retries)
                # This function handles the internal logging/checkpointing of every attempt
                state = self._execute_step_with_resilience(step, state)

                # Success handling
                self._finalize_span(span, StepStatus.COMPLETED, state)
                logger.info(f"Step '{step.name}' completed successfully.")

            except RetryError as e:
                # Failure handling after max retries (Self-healing - Report Section 3.2)
                # The final failure is already logged by _execute_step_with_resilience
                error_message = f"Step '{step.name}' failed permanently after max retries."
                logger.error(error_message)

                state.status = StepStatus.FAILED
                self._finalize_span(span, StepStatus.FAILED, state, error_message)
                self._finalize_trace(trace, StepStatus.FAILED)

                # Final checkpoint before exiting
                state.checkpoint(self.checkpoint_dir)
                return state

        # Workflow completion
        state.status = StepStatus.COMPLETED
        state.current_step = None
        state.checkpoint(self.checkpoint_dir)
        self._finalize_trace(trace, StepStatus.COMPLETED)
        logger.info(f"Workflow '{state.workflow_name}' completed successfully.")
        return state

    def _execute_step_with_resilience(self, step: WorkflowStep, state: WorkflowState) -> WorkflowState:
        """
        Wraps step execution with retry logic. Crucially, it logs and checkpoints EVERY attempt.
        """
        policy: ResiliencePolicy = step.agent.resilience_policy

        # Configure tenacity based on the agent's policy
        retryer = Retrying(
            stop=stop_after_attempt(policy.max_retries),
            wait=wait_exponential(multiplier=1, min=policy.retry_wait_min_seconds, max=policy.retry_wait_max_seconds),
            reraise=True
        )

        # Calculate the starting attempt number if resuming mid-retries
        base_attempt_num = self._get_next_base_attempt_number(state, step.name)

        def attempt_wrapper():
            # Calculate the current attempt number within this tenacity session
            tenacity_attempt_num = retryer.statistics.get('attempt_number', 1)
            # Total attempt number across sessions (for logging/checkpointing)
            current_attempt = base_attempt_num + tenacity_attempt_num - 1

            # Stop if we exceed the total max retries across sessions (handles edge case where policy changes)
            if current_attempt > policy.max_retries:
                 raise RuntimeError(f"Exceeded total max retries ({policy.max_retries}) across sessions.")

            logger.info(f"Attempt {current_attempt} (Max: {policy.max_retries}) for step '{step.name}'")

            # 1. Log RUNNING status and checkpoint (Durability)
            state.add_log(step.name, StepStatus.RUNNING, attempt=current_attempt)
            state.checkpoint(self.checkpoint_dir)

            try:
                # 2. Execute the actual agent logic
                new_state = step.execute(state)

                # 3. Log COMPLETED status and checkpoint
                new_state.add_log(step.name, StepStatus.COMPLETED, attempt=current_attempt)
                new_state.checkpoint(self.checkpoint_dir)
                return new_state

            except Exception as e:
                logger.warning(f"Attempt {current_attempt} failed for step '{step.name}': {e}")

                # 3. Log FAILED status and checkpoint before raising for retry
                state.add_log(step.name, StepStatus.FAILED, attempt=current_attempt, message=str(e))
                state.checkpoint(self.checkpoint_dir)
                raise # Raise to trigger tenacity retry

        # Execute the wrapper using the retryer
        return retryer(attempt_wrapper)

    def _get_start_index(self, steps: List[WorkflowStep], state: WorkflowState) -> int:
        """Determines the index to start execution from, enabling resumption."""
        if not state.execution_history:
            return 0

        # Find the last step name that appears in the history
        last_step_name = state.execution_history[-1].step_name

        try:
            # Find the index of this step in the current workflow definition
            last_step_index = next(i for i, step in enumerate(steps) if step.name == last_step_name)
        except StopIteration:
            logger.warning("Could not match last executed step in history with current workflow definition. Restarting.")
            return 0

        # Check the final status of that step (the status of the very last log entry)
        final_status = state.execution_history[-1].status

        if final_status == StepStatus.COMPLETED:
            # If completed, start from the next step
            return last_step_index + 1
        else:
            # If failed or running (crashed), restart the same step
            logger.info(f"Resuming workflow by re-running step '{last_step_name}' due to previous status: {final_status}")
            return last_step_index

    def _get_next_base_attempt_number(self, state: WorkflowState, step_name: str) -> int:
        """Determines the starting attempt number if resuming a step that previously failed."""
        # Find the last log for this specific step name
        last_log = next((log for log in reversed(state.execution_history) if log.step_name == step_name), None)

        if not last_log or last_log.status == StepStatus.COMPLETED:
            return 1

        # If the last status was FAILED or RUNNING, the next attempt starts after the last recorded attempt.
        return last_log.attempt + 1


    # --- Observability Hooks (Langfuse) ---

    def _initialize_trace(self, state: WorkflowState) -> Optional[StatefulTraceClient]:
        if not self.langfuse_client: return None
        try:
            # Use Run ID as Trace ID for idempotency/resumption
            return self.langfuse_client.trace(
                name=f"FSA_Workflow_{state.workflow_name}", id=str(state.run_id),
                metadata={"start_context": state.context}, tags=["orchestration", "fsa_v1"]
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Langfuse trace: {e}"); return None

    def _finalize_trace(self, trace: Optional[StatefulTraceClient], status: StepStatus):
        if trace:
            score_value = 1.0 if status == StepStatus.COMPLETED else 0.0
            trace.score(name="workflow_success", value=score_value)

    def _initialize_span(self, trace: Optional[StatefulTraceClient], step: WorkflowStep, state: WorkflowState):
         if not trace: return None
         try:
             return trace.span(
                 name=f"Step_{step.name}",
                 metadata={
                     "agent": step.agent.name,
                     "policy": step.agent.define_policy(),
                     "resilience_policy": step.agent.resilience_policy.model_dump()
                 }
            )
         except Exception as e:
            logger.warning(f"Failed to initialize Langfuse span: {e}"); return None

    def _finalize_span(self, span, status: StepStatus, state: WorkflowState, error_message: Optional[str] = None):
        if span:
            if error_message:
                 span.update(output={"error": error_message})
            score_value = 1.0 if status == StepStatus.COMPLETED else 0.0
            span.score(name="step_success", value=score_value)
            span.end()
