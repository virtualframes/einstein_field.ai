# src/fsa/ingestion/arxiv_fetcher.py
import arxiv
import hashlib
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
from fsa.core.models import Document, DocumentSource
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class ArxivFetcher:
    def __init__(self):
        self.client = arxiv.Client()

    @retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _fetch_pdf_content(self, pdf_url: str) -> bytes:
        """Fetches the PDF content from the URL with retries."""
        response = requests.get(pdf_url)
        response.raise_for_status()
        return response.content

    def fetch_by_id(self, arxiv_id: str) -> Tuple[Document, bytes]:
        """Fetches metadata and the PDF content for a given arXiv ID."""
        search = arxiv.Search(id_list=[arxiv_id])
        try:
            paper = next(self.client.results(search))
        except StopIteration:
            raise ValueError(f"ArXiv paper with ID {arxiv_id} not found.")
        except Exception as e:
            logger.error(f"Error fetching ArXiv metadata for {arxiv_id}: {e}")
            raise

        logger.info(f"Fetching PDF for {arxiv_id} from {paper.pdf_url}")
        pdf_content = self._fetch_pdf_content(paper.pdf_url)

        # Calculate hash for immutability/provenance
        content_hash = hashlib.sha256(pdf_content).hexdigest()

        doc = Document(
            source_url=paper.entry_id,
            title=paper.title,
            authors=[author.name for author in paper.authors],
            source_type=DocumentSource.ARXIV,
            raw_content_hash=content_hash,
            metadata={
                "published": paper.published.isoformat(),
                "summary": paper.summary,
            }
        )
        return doc, pdf_content
