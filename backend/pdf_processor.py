# pdf_processor.py
from mistral_converter import pdf_to_markdown_mistral
from semantic_chunking import chunk_semantic

def process_pdf(pdf_bytes: bytes) -> dict:
    """
    Process a patent PDF:
      - Convert to Markdown text using Mistral OCR.
      - Perform semantic chunking.
    Returns a dictionary with full text and chunks.
    """
    markdown_text = pdf_to_markdown_mistral(pdf_bytes)
    chunks = chunk_semantic(markdown_text)
    return {
        "full_text": markdown_text,
        "chunks": chunks
    }
