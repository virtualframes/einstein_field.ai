# Jules Agent System

This repository contains a runnable, concrete Jules coding agent that boots a minimal stack, performs an extractor->planner->verifier test flow, and emits signed provenance events.

## How to run locally

1.  **Clone the repository.**
2.  **Set up the environment.** Copy the `.env.example` file to `.env`. The default values are suitable for local development.
    ```bash
    cp .env.example .env
    ```
3.  **Start the stack.** Use `docker-compose` to build and run the backend, database, and Jules agent.
    ```bash
    docker-compose up --build
    ```
    The backend will be available at `http://localhost:8000`, and the Jules agent will run its bootstrap flow.

## How to verify agent behavior

1.  **Inspect events.** After running `docker-compose up`, you can inspect the events emitted by the Jules agent.
    ```bash
    curl http://localhost:8000/events
    ```
    You should see `intent`, `submission`, `verify`, `checkpoint`, and `pr_open` events.

2.  **Run unit tests.** You can run the unit tests locally.
    ```bash
    pip install -r backend/requirements.txt
    pytest -q tests/test_flow.py
    ```

3.  **Run advanced integration tests.**
    ```bash
    pytest -q tests/jules/test_advanced.py
    ```

## Project Structure

-   `backend/`: The FastAPI backend application.
-   `agents/`: Contains the Jules agent and the efai-agent CLI.
-   `docker-compose.yml`: Defines the services for the application stack.
-   `.github/workflows/`: Contains the CI workflows.
-   `tests/`: Contains the unit and integration tests.
-   `scripts/`: Contains utility scripts, such as the conflict checker.
