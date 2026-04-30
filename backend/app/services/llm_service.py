import requests
import json
import re


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

def extract_json_array(raw: str):
    start = raw.find("[")
    if start == -1:
        return None

    bracket_count = 0
    for i in range(start, len(raw)):
        if raw[i] == "[":
            bracket_count += 1
        elif raw[i] == "]":
            bracket_count -= 1

        if bracket_count == 0:
            json_str = raw[start:i+1]
            try:
                return json.loads(json_str)
            except Exception as e:
                print("❌ JSON parse error:", e)
                print("BAD JSON:", json_str)
                return None

    return None

def validate_questions(questions):
    valid = []

    for q in questions:
        if (
            isinstance(q, dict)
            and "question" in q
            and isinstance(q.get("options"), list)
            and len(q["options"]) == 3
            and q.get("correct_answer") in q["options"]
        ):
            valid.append(q)

    return valid

def extract_questions(raw: str):
    objects = re.findall(r"\{[\s\S]*?\}", raw)

    results = []

    for obj in objects:
        try:
            parsed = json.loads(obj)

            if (
                isinstance(parsed, dict)
                and "question" in parsed
                and isinstance(parsed.get("options"), list)
                and len(parsed["options"]) == 3
            ):
                results.append(parsed)

        except:
            continue

    return results

def generate_questions_from_context(context: str, num_questions: int, mode: str):
    difficulty = "easy and medium" if mode == "study" else "hard"

    prompt = f"""
You are an expert teacher.

Based ONLY on the context below, generate {num_questions} {difficulty} questions.

STRICT RULES (MUST FOLLOW):
- Return ONLY valid JSON
- DO NOT write anything outside JSON
- ALWAYS include exactly 3 options
- NEVER leave fields empty
- correct_answer MUST be one of the options
- topic MUST NOT be empty

FORMAT:

[
  {{
    "question": "string",
    "options": ["option1", "option2", "option3"],
    "correct_answer": "one of the options",
    "topic": "short topic name"
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
            "stream": False,
            "options": {
                "temperature": 0.5,
                "num_predict": 500  
            }
        }
    )

    raw = response.json().get("response", "").strip()


    parsed = extract_questions(raw)


    if parsed and len(parsed) > 0:
        return parsed

    print("❌ PARSING FAILED")
    print("RAW:", raw)

    return [{
        "question": "Fallback question",
        "options": ["Option 1", "Option 2", "Option 3"],
        "topic": "general"
    }]


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