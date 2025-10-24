# DeepSeek Agent

This document describes how to use the DeepSeek agent and its associated tools.

## Setup

To use the DeepSeek agent, you must first add your DeepSeek API key to the environment variables.

```
export DEEPSEEK_API_KEY=<your_api_key>
```

This project also uses NLTK’s punkt tokenizer. Ensure it’s downloaded via `python -m nltk.downloader punkt` or included in CI workflows.

## How to Run

You can run the DeepSeek agent using the `jules` CLI.

### Summarization

```
python -m agents.jules.cli summarize --docs <path_to_doc> --prompt "Summarize this document."
```

### OCR

The OCR tool is not yet integrated with the CLI.

## Provenance

The DeepSeek agent emits provenance artifacts for each API call. These artifacts are stored in the `agents/provenance/deepseek` directory.
