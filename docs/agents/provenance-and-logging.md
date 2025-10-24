# Provenance and Logging

This document describes the provenance and logging standards for the Jules agents.

## Provenance

Provenance artifacts are signed JSON files that record the inputs, outputs, and metadata of an agent's execution. They are stored in the `.provenance` directory at the root of the repository.

### Checkpoint Format

Agent progress checkpoints are stored in the `agents/progress` directory. They are JSON files with the following format:

```json
{
  "run_id": "string",
  "agent_name": "string",
  "step_index": "integer",
  "action": "string",
  "timestamp_utc": "string",
  "inputs_hash": "string",
  "outputs_hash": "string",
  "status": "string"
}
```

## Replay

To replay a provenance run, use the `jules reproduce` command with the provenance ID:

```
jules reproduce <provenance_id> --output-dir /tmp/replay
```
