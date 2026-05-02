import random

from typing import TypedDict
from langgraph.graph import StateGraph
from app.services.llm_service import  call_llm



class LearningState(TypedDict):
    question: str
    user_answer: str
    correct_answer: str
    difficulty: str
    is_correct: bool
    needs_explanation: bool
    next_action: str
    topic: str
    context: str
    score: int       
    explanation: str


def evaluate_node(state: LearningState):
    is_correct = state["user_answer"].strip().lower() == state["correct_answer"].strip().lower()

    score = 10 if is_correct else 0

    return {"is_correct": is_correct, "score": score}



def decide_node(state: LearningState):
    if not state["is_correct"]:
        return {"next_action": "repeat", "needs_explanation": True}
    diff = state.get("difficulty", "medium")
    if diff == "easy":
        return {"next_action": "harder", "needs_explanation": False}
    elif diff == "medium":
        return {"next_action": "harder", "needs_explanation": False}
    else:
        return {"next_action": "same_level", "needs_explanation": False}
    

    
def explain_node(state: LearningState):
    prompt = f"""You are a concise tutor giving instant feedback after a wrong quiz answer.

Question: {state["question"]}
Correct answer: {state["correct_answer"]}
Topic: {state["topic"]}

Write 1-2 sentences MAX that:
- State what the correct answer means or why it's right
- Are direct and factual, no filler phrases

Rules:
- Do NOT say "the student", "you answered", "don't worry", "great question", or anything encouraging
- Do NOT mention what the wrong answer was
- Start directly with the explanation, like: "[Correct answer] is correct because..."
- Maximum 2 sentences
"""
    explanation = call_llm(prompt)
    return {"explanation": explanation}


def route_after_decision(state: LearningState):
    return "explain" if state.get("needs_explanation") else "end"


def build_agent():
    graph = StateGraph(LearningState)

    graph.add_node("evaluate", evaluate_node)   
    graph.add_node("decide", decide_node)
    graph.add_node("explain", explain_node)
    graph.add_node("end", lambda x: x)

    graph.set_entry_point("evaluate")           
    graph.add_edge("evaluate", "decide")
    graph.add_conditional_edges(
        "decide",
        route_after_decision,
        {"explain": "explain", "end": "end"}
    )
    graph.add_edge("explain", "end")
    graph.set_finish_point("end")

    return graph.compile()


def select_next_question(session, action):
    questions = session["questions"]
    current = questions[session["current_index"]]

    current_diff = current.get("difficulty", "medium")

    if action == "harder":
        target = "hard" if current_diff != "hard" else "hard"

    elif action == "repeat":
        return current

    elif action == "focus_weak":
        weak_topic = max(session["weak_topics"], key=session["weak_topics"].get, default=None)
        filtered = [q for q in questions if q.get("topic") == weak_topic]
        return random.choice(filtered) if filtered else current

    else:  
        target = current_diff

    pool = [q for q in questions if q.get("difficulty") == target]

    if not pool:
        return current  

    return random.choice(pool)
