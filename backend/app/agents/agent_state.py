import requests
from typing import TypedDict
from app.routers.evaluate import evaluate_answer
from langgraph.graph import StateGraph
from app.services.rag_service import retrieve_context
from app.services.llm_service import generate_questions_from_context



class LearningState(TypedDict):
    question: str
    user_answer: str
    evaluation: dict
    next_action: str
    topic: str
    context: str

def evaluate_node(state: LearningState):
    evaluation = evaluate_answer(
        state["question"],
        state["user_answer"],
        None,
        None
    )

    return {
        "evaluation": evaluation
    }

def decision_node(state: LearningState):
    score = state["evaluation"].get("score", 0)
    topic = state.get("topic")
    weak_topics = state.get("weak_topics", {})

    if weak_topics.get(topic, 0) >= 2:
        action = "focus_weak"

    elif score < 5:
        action = "repeat"

    elif score < 8:
        action = "same_level"

    else:
        action = "harder"

    needs_explanation = score < 5

    return {
        "next_action": action,
        "needs_explanation": needs_explanation
    }

def generate_node(state: LearningState):
    action = state["next_action"]
    topic = state["topic"]

    if action == "focus_weak":
        query = topic + " basics explanation examples"

    elif action == "repeat":
        query = topic

    elif action == "harder":
        query = topic + " advanced concepts"

    else:
        query = "next concept"

    context, _ = retrieve_context(query)

    questions = generate_questions_from_context(context, 1, "study")

    next_q = questions[0]

    return {
        "question": next_q["question"],
        "topic": next_q.get("topic", topic),
        "context": context
    }

def explain_node(state: LearningState):
    score = state["evaluation"].get("score", 0)

    if score >= 5:
        return {}

    question = state["question"]
    context = state.get("context")

    prompt = f"""
        Explain the concept clearly and simply.

        Question:
        {question}

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

    explanation = response.json().get("response", "")

    return {
        "explanation": explanation
    }

def route_after_decision(state: LearningState):
    if state.get("needs_explanation"):
        return "explain"
    return "generate"


graph = StateGraph(LearningState)

graph.add_node("evaluate", evaluate_node)
graph.add_node("decide", decision_node)
graph.add_node("explain", explain_node)
graph.add_node("generate", generate_node)


graph.set_entry_point("evaluate")

graph.add_edge("evaluate", "decide")

graph.add_conditional_edges(
    "decide",
    route_after_decision,
    {
        "explain": "explain",
        "generate": "generate"
    }
)

graph.add_edge("explain", "generate")

graph.set_finish_point("generate")

app = graph.compile()