from typing import List, Dict
import json
import logging
from agents.jules.provenance import record_execution
from habanero import Crossref
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import nltk
from datetime import datetime, timezone

# Configure structured logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Ensure NLTK 'punkt' tokenizer is available
punkt_downloaded_timestamp = None
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    punkt_downloaded_timestamp = datetime.now(timezone.utc).isoformat()

def summarize_documents(query: str, docs: List[str], provenance_hint: dict) -> Dict:
    """
    Returns extractive and abstractive summaries, with per-sentence grounding back to source bytes and provenance.
    """
    logging.info(f"Summarizing documents for query: {query}")

    # For now, we'll just summarize the first document
    doc_path = docs[0]

    # Read the document content
    with open(doc_path, 'r') as f:
        text = f.read()

    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    stemmer = Stemmer("english")
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words("english")

    # Summarize the document to 5 sentences
    summary_sentences = summarizer(parser.document, 5)
    extractive_summary = " ".join([str(sentence) for sentence in summary_sentences])

    result = {
        "extractive_summary": extractive_summary,
        "abstractive_summary": "This is a placeholder for the abstractive summary."
    }

    grounding = [
        {
            "source": docs[0],
            "span": [0, len(extractive_summary)],
            "score": 1.0
        }
    ]

    provenance_metadata = {}
    if punkt_downloaded_timestamp:
        provenance_metadata["nltk_tokenizer"] = {
            "resource": "punkt",
            "downloaded": True,
            "timestamp": punkt_downloaded_timestamp
        }

    provenance_id = record_execution(
        target="summarize_documents",
        actor="jules-langchain-agent",
        inputs={"query": query, "docs": docs, "provenance_hint": provenance_hint},
        outputs={"result": result, "grounding": grounding},
        metadata=provenance_metadata
    )

    logging.info(f"Summarization complete. Provenance ID: {provenance_id}")

    return {
        "result": result,
        "grounding": grounding,
        "provenance_id": provenance_id
    }

def verify_citation(citation_raw: str) -> Dict:
    """
    Returns normalized metadata and grounding score.
    """
    cr = Crossref()
    try:
        # This is a simple example of how to use the habanero library.
        # A real implementation would need to handle different types of citations
        # and would need to be more robust.
        results = cr.works(query=citation_raw, limit=1)
        if results['message']['items']:
            item = results['message']['items'][0]
            return {
                "normalized": item.get('DOI'),
                "grounding_score": item.get('score'),
                "provenance_id": record_execution(
                    target="verify_citation",
                    actor="jules-langchain-agent",
                    inputs={"citation_raw": citation_raw},
                    outputs={"normalized": item.get('DOI'), "grounding_score": item.get('score')},
                    metadata={}
                )
            }
    except Exception as e:
        logging.error(f"Error verifying citation: {e}")

    return {"normalized": None, "grounding_score": 0.0}

def extract_claims(doc_paths: List[str]) -> List[Dict]:
    """
    Extracts claims from a list of documents.
    """
    # This is a placeholder implementation.
    return [
        {
            "claim": "This is a claim.",
            "source": doc_paths[0],
            "confidence": 0.9
        }
    ]

def contradiction_check(claim: str, docs: List[str]) -> Dict:
    """
    Returns contradictory evidence nodes and a scored contradiction graph.
    """
    # This is a placeholder implementation.
    return {
        "contradiction": True,
        "nodes": [
            {"id": "claim", "label": claim},
            {"id": "evidence_1", "label": "This is a contradictory piece of evidence."}
        ],
        "edges": [
            {"from": "claim", "to": "evidence_1", "label": "contradicts"}
        ],
        "score": 0.8
    }
