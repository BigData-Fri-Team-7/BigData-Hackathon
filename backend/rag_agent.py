import os
from dotenv import load_dotenv
from typing import TypedDict, Optional, Dict, Any
import re

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from llm_chat import get_llm_response
import pinecone
from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "bigdata-hackathon")

pc = Pinecone(api_key=PINECONE_API_KEY, spec=ServerlessSpec(cloud="aws", region=PINECONE_REGION))
model = SentenceTransformer("all-MiniLM-L6-v2")

def query_embeddings(query_text: str, top_k: int) -> dict:
    index = pc.Index(PINECONE_INDEX_NAME)
    query_vector = model.encode(query_text).tolist()
    try:
        response = index.query(
            vector=query_vector,
            top_k=top_k,
            include_metadata=True
        )
        return {"matches": response.get("matches", [])}
    except Exception as e:
        print(f"Error querying Pinecone index '{PINECONE_INDEX_NAME}': {e}")
        return {"matches": []}

class RAGState(TypedDict, total=False):
    question: str
    top_k: Optional[int]
    rag_output: str

def rag_agent(state: RAGState) -> Dict[str, Any]:
    query = state.get("question", "Summarize patent content.")
    
    # Retrieve internal context from Pinecone
    index = pc.Index(PINECONE_INDEX_NAME)
    stats = index.describe_index_stats()
    total_records = stats.get("total_vector_count", 0)
    
    if total_records == 0:
        internal_context = ""
    else:
        # Set top_k to total number of vectors to retrieve all of them
        results = query_embeddings(query_text=query, top_k=total_records)
        chunks = [
            m.get("metadata", {}).get("text", "") or m.get("text", "")
            for m in results.get("matches", [])
        ]
        internal_context = " ".join(chunks)
    
    # Use only internal data for generating the report
    combined_context = internal_context
    
    pdf_data = {"pdf_content": combined_context, "tables": []}
    response = get_llm_response(pdf_data, query, "gpt-4o")
    state["rag_output"] = response["answer"]
    return state

def build_graph():
    builder = StateGraph(RAGState)
    builder.add_node("RAGAgent", RunnableLambda(rag_agent))
    builder.set_entry_point("RAGAgent")
    builder.add_edge("RAGAgent", END)
    return builder.compile()

if __name__ == "__main__":
    graph = build_graph()
    sample_state = {
        "question": "Generate a research report for patent US9123456",
        "top_k": None  # Not used; we retrieve all records
    }
    result = graph.invoke(sample_state)
    print("\nRAG Agent Output:\n")
    print(result.get("rag_output"))
