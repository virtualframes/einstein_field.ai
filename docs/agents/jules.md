# Jules Agent Contract

## Purpose

The Jules agent is responsible for the following:

- Fetching the latest submission from the backend.
- Running a SymPy check on the submission.
- Emitting `verify` and `debug` events based on the result of the SymPy check.
- Creating a checkpoint artifact.
- Opening a pull request stub.

## Inputs

- **Backend URL**: The URL of the backend service, provided via the `BACKEND_URL` environment variable.
- **Agent Secret**: A secret key used for signing events, provided via the `EFAIAGENTSECRET` environment variable.

## Outputs

- **Events**: The agent emits the following events to the backend:
  - `checkpoint`: Indicates that a checkpoint artifact has been created.
  - `pr_open`: Indicates that a pull request stub has been created.
  - `verify`: Indicates the result of the SymPy check.
  - `debug`: Emitted when the SymPy check fails.
- **Log Messages**: The agent produces structured log messages in JSON format.

## Error Conditions

- **No Submission Found**: If no submission is found, the agent will log a warning and exit.
- **HTTP Errors**: If the agent encounters an HTTP error when communicating with the backend, it will raise an exception and terminate.
