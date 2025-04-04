from typing import List
import nltk
import os
from nltk.tokenize import sent_tokenize
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Dynamically add nltk_data path
nltk_path = os.path.join(os.path.dirname(__file__), "nltk_data")
nltk.data.path.append(nltk_path)

# Ensure that the required nltk resource is available
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", download_dir=nltk_path)

model = SentenceTransformer("all-MiniLM-L6-v2")

def chunk_semantic(
    markdown_content: str,
    chunk_size: int = 300,
    similarity_threshold: float = 0.75
) -> List[str]:
    sentences = sent_tokenize(markdown_content)
    embeddings = model.encode(sentences, convert_to_numpy=True)

    chunks = []
    current_sents = []
    current_embeds = []

    for sent, emb in zip(sentences, embeddings):
        if not current_sents:
            current_sents.append(sent)
            current_embeds.append(emb)
            continue

        avg_embed = np.mean(current_embeds, axis=0, keepdims=True)
        sim = cosine_similarity([emb], avg_embed)[0][0]
        prospective = " ".join(current_sents + [sent])

        if sim >= similarity_threshold and len(prospective) <= chunk_size:
            current_sents.append(sent)
            current_embeds.append(emb)
        else:
            chunks.append(" ".join(current_sents))
            current_sents = [sent]
            current_embeds = [emb]

    if current_sents:
        chunks.append(" ".join(current_sents))

    return chunks
