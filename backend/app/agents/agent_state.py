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
        return {"next_action": "same_level", "needs_explanation": True}
    
    diff = state.get("difficulty", "medium")
    next_diff = {"easy": "medium", "medium": "hard"}.get(diff, "same_level")
    action = "harder" if next_diff != "same_level" else "same_level"
   
    return {"next_action": action, "needs_explanation": False}
    

    
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
    answered_questions = {a["question"]["question"] for a in session["answers"]}

    current = session["current_question"] 
    current_diff = current.get("difficulty", "medium")

    # Filter out already-answered questions
    unanswered = [q for q in questions if q["question"] not in answered_questions]

    if not unanswered:
        return current

    if action == "harder":
        next_diff = {"easy": "medium", "medium": "hard"}.get(current_diff, "hard")
        pool = [q for q in unanswered if q.get("difficulty") == next_diff]
        if not pool:
            pool = unanswered  

    elif action == "focus_weak":
        weak_topic = max(session["weak_topics"], key=session["weak_topics"].get, default=None)
        pool = [q for q in unanswered if q.get("topic") == weak_topic]
        if not pool:
            pool = unanswered

    else:  
        pool = [q for q in unanswered if q.get("difficulty") == current_diff]
        if not pool:
            pool = unanswered

    return random.choice(pool)
