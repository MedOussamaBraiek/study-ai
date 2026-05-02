from sentence_transformers import SentenceTransformer

model = None

def get_model():
    global model
    if model is None:
        model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

def embed_texts(texts: list[str]):
    m = get_model()
    return m.encode(texts)

def embed_query(query: str):
    m = get_model()
    return m.encode([query])