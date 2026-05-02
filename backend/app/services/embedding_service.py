import requests
import os
import numpy as np

HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def embed_texts(texts: list[str]):
    response = requests.post(API_URL, headers=headers, json={"inputs": texts, "options": {"wait_for_model": True}})
    return np.array(response.json())

def embed_query(query: str):
    return embed_texts([query])