import json
from pathlib import Path

def ingest_ci_failure_event(event_path):
    """
    Ingests a CI failure event from a JSON file.
    """
    event_data = json.loads(Path(event_path).read_text())
    print(f"Ingested CI failure event for job: {event_data.get('job_name')}")
    # In a real implementation, this would trigger further processing,
    # such as routing the event to the appropriate recovery agent.
    return event_data

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("event_path", help="Path to the CI failure event JSON file.")
    args = parser.parse_args()
    ingest_ci_failure_event(args.event_path)
