from sentence_transformers import SentenceTransformer

def get_model():
    global model
    if model is None:
        model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

def embed_texts(texts: list[str]):
    get_model()
    return model.encode(texts)

def embed_query(query: str):
    get_model()
    return model.encode([query])