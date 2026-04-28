from app.services.embedding_service import embed_query
from app.services.vector_store import search

def retrieve_context(question: str):
    q_embedding = embed_query(question)
    results = search(q_embedding)

    context = "\n\n".join([r["text"] for r in results])

    return context, results