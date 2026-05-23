import os
try:
    import posthog
    posthog.capture = lambda *args, **kwargs: None
except ImportError:
    pass
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(CURRENT_DIR, "chroma_db")
MASTER_PLANS_PATH = os.path.join(CURRENT_DIR, "data", "master_plans.txt")

# Global collection handles
chroma_client = None
collection = None

def initialize_rag():
    """
    Initializes ChromaDB persistent client, creates the collection,
    and loads the parsed master plans if the collection is empty.
    """
    global chroma_client, collection
    
    # Establish persistent client mapping to chroma_db folder
    chroma_client = chromadb.PersistentClient(
        path=DB_PATH,
        settings=chromadb.Settings(anonymized_telemetry=False)
    )
    
    # Core embedding model: SentenceTransformer with all-MiniLM-L6-v2
    embedding_function = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    collection = chroma_client.get_or_create_collection(
        name="zoning_infrastructure",
        embedding_function=embedding_function
    )
    
    # Check count: if 0, index master plans
    try:
        count = collection.count()
    except Exception:
        count = 0

    if count == 0:
        if os.path.exists(MASTER_PLANS_PATH):
            with open(MASTER_PLANS_PATH, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Split on double newlines
            raw_chunks = content.split("\n\n")
            documents = []
            metadatas = []
            ids = []
            
            chunk_id_counter = 0
            for chunk in raw_chunks:
                clean_chunk = chunk.strip()
                if clean_chunk:
                    documents.append(clean_chunk)
                    metadatas.append({
                        "source": "master_plans",
                        "chunk_id": chunk_id_counter
                    })
                    ids.append(f"chunk_{chunk_id_counter}")
                    chunk_id_counter += 1
            
            if documents:
                collection.add(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )

def query_rag_context(query: str, n_results: int = 3) -> str:
    """
    Queries ChromaDB and returns the formatted grounding context or fallback message.
    """
    global collection
    if collection is None:
        try:
            initialize_rag()
        except Exception:
            return "No specific zoning or infrastructure data found for this query."
            
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        docs = results.get("documents", [])
        if docs and len(docs[0]) > 0:
            flattened = docs[0]
            return "GROUNDING CONTEXT:\n" + "\n---\n".join(flattened)
    except Exception:
        pass
        
    return "No specific zoning or infrastructure data found for this query."

# Attempt automatic initialization on execution/import
try:
    initialize_rag()
except Exception:
    pass
