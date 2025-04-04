# embedding_manager.py
import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# Load environment variables from the .env file
load_dotenv()

# Retrieve Pinecone configuration from environment variables
API_KEY = os.getenv("PINECONE_API_KEY")
REGION = os.getenv("PINECONE_REGION", "us-east-1")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "bigdata-hackathon")

# Initialize the Pinecone client
pc = Pinecone(api_key=API_KEY)

# Initialize the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def upsert_embeddings(chunks: list, metadata: dict):
    """
    Encodes text chunks, clears the existing index if vectors are present,
    and upserts the new embeddings in batches to the Pinecone index.
    
    Parameters:
        chunks (list): A list of text chunks.
        metadata (dict): Metadata to associate with each vector (e.g. source identifier).
    """
    vectors = []
    for i, chunk in enumerate(chunks):
        embedding = model.encode(chunk).tolist()
        vectors.append({
            "id": f"{metadata.get('source')}-{i}",
            "values": embedding,
            "metadata": {**metadata, "chunk_index": i, "text": chunk}
        })

    # Retrieve the index
    index = pc.Index(INDEX_NAME)
    
    # If there are already vectors in the index, clear them
    try:
        stats = index.describe_index_stats()
        if stats.get("total_vector_count", 0) > 0:
            print(f"Clearing index '{INDEX_NAME}' before upserting...")
            index.delete(delete_all=True)
    except Exception as e:
        print(f"Warning: Could not describe/delete index '{INDEX_NAME}': {e}")

    # Upsert vectors in batches
    batch_size = 50
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        for attempt in range(3):
            try:
                index.upsert(vectors=batch)
                print(f"Upserted batch {i // batch_size + 1}")
                break  # Break if successful
            except Exception as e:
                print(f"Error upserting batch {i // batch_size + 1}, attempt {attempt+1}: {e}")
                time.sleep(2 ** attempt)
                if attempt == 2:
                    print("Skipping batch due to repeated errors.")
    print(f"Upserted all {len(vectors)} vectors to index '{INDEX_NAME}'.")

"""
def query_pinecone(query_text: str, top_k: int = 500) -> dict:

    index = pc.Index(INDEX_NAME)
    query_vector = model.encode(query_text).tolist()

    try:
        response = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        return {"matches": response.get("matches", [])}
    except Exception as e:
        print(f"Error querying Pinecone index '{INDEX_NAME}': {e}")
        return {"matches": []}
"""
def query_pinecone(query_text: str = "", top_k: int = None) -> dict:
    
    index = pc.Index(INDEX_NAME)

    try:
        if top_k is None:
            # Get total number of vectors
            stats = index.describe_index_stats()
            total_vectors = stats.get("total_vector_count", 0)
            if total_vectors == 0:
                return {"matches": []}
            
            # Create a neutral query vector (e.g., zero vector)
            dim = len(model.encode("sample text").tolist())
            query_vector = [0.0] * dim

            # Retrieve all vectors
            response = index.query(
                vector=query_vector,
                top_k=total_vectors,
                include_metadata=True
            )
            return {"matches": response.get("matches", [])}
        else:
            # Perform standard similarity search
            query_vector = model.encode(query_text).tolist()
            response = index.query(
                vector=query_vector,
                top_k=top_k,
                include_metadata=True
            )
            return {"matches": response.get("matches", [])}

    except Exception as e:
        print(f"Error querying Pinecone index '{INDEX_NAME}': {e}")
        return {"matches": []}



if __name__ == "__main__":
    # Example usage (this block is executed when running the file directly)
    sample_chunks = ["Example text chunk one.", "Another example text chunk."]
    sample_metadata = {"source": "sample_pdf"}
    upsert_embeddings(sample_chunks, sample_metadata)
    
    sample_query = "Example query text."
    results = query_pinecone(sample_query)
    print("Query results:", results)
