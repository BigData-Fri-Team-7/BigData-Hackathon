# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI / GPT-4O
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# SerpApi for Google Patents search
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
# Mistral OCR API
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
# Pinecone API settings
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")
# New Pinecone index name
PINECONE_INDEX_NAME = "bigdata-hackathon"
# AWS S3 credentials and bucket
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
