from sentence_transformers import SentenceTransformer
import torch
import os

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

model = None

def get_model():
    global model
    if model is None:
        model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
    return model

def embed_texts(texts: list[str]):
    m = get_model()
    return m.encode(texts)

def embed_query(query: str):
    m = get_model()
    return m.encode([query])