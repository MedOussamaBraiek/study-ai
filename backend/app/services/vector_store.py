import faiss
import numpy as np

index = None
texts = []
topics = []

def create_index(embeddings, chunks):
    global index, texts, topics

    dimension = embeddings.shape[1]
    # for example (10, 384) : 10 chunks and 384 nbrs per chunk so shape[1] = 384
    index = faiss.IndexFlatL2(dimension)
    # creates FAISS index / Flat → exact search / L2 → Euclidean distance 
    # compare vectors using geometric distance
    index.add(np.array(embeddings))
    # adds all chunk embeddings into FAISS
    # save vectors into searchable memory

    texts = [c["text"] for c in chunks]
    topics = [c["topic"] for c in chunks]


def search(query_embedding, k=3):
    D, I = index.search(np.array(query_embedding), k)
    
    results = []
    for i in I[0]:
        results.append({
            "text": texts[i],
            "topic": topics[i]
        })
    
    return results