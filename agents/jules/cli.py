import argparse
import json
import sys
from agents.jules.validator import validate_notebook
from agents.jules.zotero_sync import sync as sync_zotero_main
from agents.jules.agents.tools import summarize_documents as summarize_documents_main

def validate(args):
    """Validate a notebook."""
    result = validate_notebook(args.notebook, baseline_path=args.baseline)
    print(json.dumps(result, indent=2))
    if result["status"] == "failure":
        sys.exit(1)

def run(args):
    """Placeholder for the run command."""
    print(json.dumps({"status": "run successful", "notebook": args.notebook}))

def sync_zotero(args):
    """Sync Zotero citations."""
    result = sync_zotero_main(args.api_key, args.user, args.collections.split(','))
    print(json.dumps(result, indent=2))

def summarize(args):
    """Summarize documents."""
    result = summarize_documents_main(args.prompt, args.docs, {})
    print(json.dumps(result, indent=2))

def serve_dashboard(args):
    """Placeholder for the serve-dashboard command."""
    print(json.dumps({"status": "dashboard served", "port": args.port}))

def main():
    parser = argparse.ArgumentParser(description="Jules CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Validate command
    parser_validate = subparsers.add_parser("validate")
    parser_validate.add_argument("notebook", help="The notebook to validate.")
    parser_validate.add_argument("--env-spec", help="The environment spec file.")
    parser_validate.add_argument("--baseline", help="The baseline audit JSON.")
    parser_validate.add_argument("--output", help="The output audit JSON.")
    parser_validate.set_defaults(func=validate)

    # Run command
    parser_run = subparsers.add_parser("run")
    parser_run.add_argument("notebook", help="The notebook to run.")
    parser_run.add_argument("--capture-outputs", action="store_true", help="Capture the outputs.")
    parser_run.add_argument("--provenance", action="store_true", help="Generate provenance.")
    parser_run.add_argument("--commit-artefacts", action="store_true", help="Commit the artefacts.")
    parser_run.set_defaults(func=run)

    # Sync-zotero command
    parser_sync = subparsers.add_parser("sync-zotero")
    parser_sync.add_argument("--api-key", required=True, help="The Zotero API key.")
    parser_sync.add_argument("--user", required=True, help="The Zotero user ID.")
    parser_sync.add_argument("--collections", required=True, help="The Zotero collections.")
    parser_sync.set_defaults(func=sync_zotero)

    # Summarize command
    parser_summarize = subparsers.add_parser("summarize")
    parser_summarize.add_argument("--docs", nargs="+", required=True, help="The documents to summarize.")
    parser_summarize.add_argument("--prompt", required=True, help="The prompt for summarization.")
    parser_summarize.set_defaults(func=summarize)

    # Serve-dashboard command
    parser_dashboard = subparsers.add_parser("serve-dashboard")
    parser_dashboard.add_argument("--port", type=int, default=8080, help="The port for the dashboard.")
    parser_dashboard.set_defaults(func=serve_dashboard)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
