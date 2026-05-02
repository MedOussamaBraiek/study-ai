# embedding_service.py
import requests
import os
import numpy as np

HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://router.huggingface.co/hf-inference/models/sentence-transformers/all-MiniLM-L6-v2/pipeline/feature-extraction"


headers = {"Authorization": f"Bearer {HF_TOKEN}"}

def embed_texts(texts: list[str]):
    response = requests.post(API_URL, headers=headers, json={
        "inputs": texts,
        "options": {"wait_for_model": True}
    })
    
    if response.status_code != 200:
        raise Exception(f"HF API error {response.status_code}: {response.text}")
    
    if not response.text.strip():
        raise Exception("HF API returned empty response — check your HF_TOKEN")
    
    return np.array(response.json())

def embed_query(query: str):
    return embed_texts([query])