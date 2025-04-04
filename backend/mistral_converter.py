# backend/mistral_converter.py

import os
import base64
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("MISTRAL_API_KEY")
client = Mistral(api_key=API_KEY)

def pdf_to_markdown_mistral(pdf_bytes: bytes) -> str:
    """Uses Mistral OCR to extract Markdown from PDF bytes."""
    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
    data_uri = f"data:application/pdf;base64,{encoded_pdf}"

    document = {"type": "document_url", "document_url": data_uri}
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document=document,
        include_image_base64=False
    )

    pages = ocr_response.pages if hasattr(ocr_response, "pages") else []
    markdown_text = "\n\n".join(page.markdown for page in pages) if pages else "No text extracted."

    return markdown_text
