import requests
import json


def generate_answer(context: str, question: str):
    prompt = f"""
    You are a helpful assistant.

    Answer the question ONLY using the context below.
    If the answer is not in the context, say "I don't know".

    Context:
    {context}

    Question:
    {question}
    """

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]

def generate_questions_from_context(context: str, num_questions: int, mode: str):
    difficulty = "easy and medium" if mode == "study" else "hard"

    prompt = f"""
You are an expert teacher.

Based ONLY on the context below, generate {num_questions} {difficulty} questions.

Rules:
- Mode: {mode}
- If study → easy/medium
- If interview → harder
- Each question must have 3 options
- Include the correct answer

Return STRICT JSON format like this:

[
  {{
    "question": "...",
    "options": ["A", "B", "C"],
    "correct_answer": "A"
  }}
]

Context:
{context}
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }
    )

    raw = response.json().get("response", "")

    try:
        questions = json.loads(raw)
    except:
        questions = raw  

    return questions

def evaluate_answer(question: str, user_answer: str, correct_answer: str | None, context: str | None):

    prompt = f"""
You are an expert teacher evaluating a student's answer.

Your task:
- Check if the user's answer is correct or partially correct
- Give a score from 0 to 10
- Explain why
- If wrong, provide the correct answer

Rules:
- Be strict but fair
- Use ONLY the context if provided

Question:
{question}

User Answer:
{user_answer}

Correct Answer (if provided):
{correct_answer}

Context:
{context}

Return ONLY JSON:

{{
  "score": 0-10,
  "is_correct": true/false,
  "feedback": "...",
  "correct_answer": "..."
}}
"""
    
    response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    }   
    )

    raw = response.json().get("response", "")

    try:
        result = json.loads(raw)
    except:
        result = raw  

    return result