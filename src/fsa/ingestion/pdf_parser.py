# src/fsa/ingestion/pdf_parser.py
import fitz  # PyMuPDF
from fsa.core.models import Document, ParsedSection
from typing import List
import logging
import re

logger = logging.getLogger(__name__)

class PDFParser:
    # Heuristic pattern for academic headings
    SECTION_PATTERN = re.compile(r"\n(\d+(\.\d+)*\s+[A-Z][a-zA-Z\s\-]+|Abstract|Introduction|References|Conclusion|Methodology|Related Work)\n")

    def parse(self, document: Document, pdf_content: bytes) -> List[ParsedSection]:
        """
        Parses PDF content into structured sections using heuristics.
        """
        try:
            doc = fitz.open("pdf", pdf_content)
        except Exception as e:
            logger.error(f"Failed to open PDF content for document {document.id}: {e}")
            raise

        full_text = ""
        for page in doc:
            full_text += page.get_text("text")

        sections = []
        current_pos = 0
        current_title = "Preamble"
        current_level = 1

        # Logic to split the text based on the regex pattern
        for match in self.SECTION_PATTERN.finditer(full_text):
            # Capture content of the previous section
            content = full_text[current_pos:match.start()].strip()
            if content:
                sections.append(ParsedSection(
                    document_id=document.id, title=current_title, content=content, level=current_level
                ))

            # Start the new section
            current_title = match.group(1).strip()
            current_pos = match.end()

            # Determine level based on numbering (e.g., "1." vs "1.1.")
            header_start = current_title.split()[0]
            if re.match(r'^\d+(\.\d+)*$', header_start.replace('.', '')):
                 current_level = header_start.count(".") + 1
            else:
                 current_level = 1

        # Capture the last section
        content = full_text[current_pos:].strip()
        if content:
            sections.append(ParsedSection(
                document_id=document.id, title=current_title, content=content, level=current_level
            ))

        logger.info(f"Parsed {len(sections)} sections from document {document.id}.")
        return sections
