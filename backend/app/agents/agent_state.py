from typing import TypedDict
from app.routers.evaluate import evaluate_answer
from langgraph.graph import StateGraph


class LearningState(TypedDict):
    question: str
    user_answer: str
    evaluation: dict
    next_action: str

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

    if score < 5:
        action = "repeat"
    elif score < 8:
        action = "same_level"
    else:
        action = "harder"

    return {
        "next_action": action
    }

graph = StateGraph(LearningState)

graph.add_node("evaluate", evaluate_node)
graph.add_node("decide", decision_node)

graph.set_entry_point("evaluate")

graph.add_edge("evaluate", "decide")

graph.set_finish_point("decide")

app = graph.compile()