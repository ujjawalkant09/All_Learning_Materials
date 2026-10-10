"""Milestone 8 · Command-line app  (revise: steps 08, 11, 14)

Run from the folder that contains ``expense_assistant/``::

    python -m expense_assistant.cli                # agent mode: all tools, approvals, budget alerts
    python -m expense_assistant.cli --mode graph   # LangGraph router mode
    python -m expense_assistant.cli --seed         # add sample expenses first
"""

import argparse
import uuid

from dotenv import load_dotenv
from langchain.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from . import db


def new_ai_replies(messages: list) -> list[str]:
    """Text of the AI messages produced after the last human message (skips empty tool-call messages)."""
    replies = []
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            break
        if isinstance(message, AIMessage) and message.content:
            replies.append(message.content)
    return list(reversed(replies))


def resolve_interrupts(agent, result: dict, config: dict, decide=input) -> dict:
    """Ask the human about every paused tool call until nothing is pending.

    Args:
        decide: function that shows a question and returns the answer; ``input`` in the CLI, a lambda in tests.
    """
    while "__interrupt__" in result:
        decisions = []
        for interrupt in result["__interrupt__"]:
            for action in interrupt.value["action_requests"]:
                answer = decide(f"Approve {action['name']}({action['args']})? [y/n] ").strip().lower()
                if answer.startswith("y"):
                    decisions.append({"type": "approve"})
                else:
                    decisions.append({"type": "reject", "message": "The user rejected this action."})
        result = agent.invoke(Command(resume={"decisions": decisions}), config)
    return result


def chat_loop(mode: str, thread_id: str) -> None:
    """Read user input until 'exit' and print the assistant's replies."""
    if mode == "graph":
        from .graph import build_default_graph

        app = build_default_graph()
    else:
        from .agent import build_agent
        from .middleware import build_middleware

        app = build_agent(checkpointer=InMemorySaver(), middleware=build_middleware())

    config = {"configurable": {"thread_id": thread_id}}
    print(f"Expense assistant ({mode} mode). Type 'exit' to quit.")
    while (text := input("You: ").strip()).lower() != "exit":
        if not text:
            continue
        result = app.invoke({"messages": [HumanMessage(text)]}, config)
        result = resolve_interrupts(app, result, config)
        for reply in new_ai_replies(result["messages"]):
            print("Assistant:", reply)


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with your expense assistant")
    parser.add_argument("--mode", choices=["agent", "graph"], default="agent")
    parser.add_argument("--thread", default=str(uuid.uuid4()), help="conversation id (reuse to continue)")
    parser.add_argument("--seed", action="store_true", help="insert sample expenses if the DB is empty")
    args = parser.parse_args()

    load_dotenv()
    db.init_db()
    if args.seed:
        db.seed_sample_data()
    chat_loop(args.mode, args.thread)


if __name__ == "__main__":
    main()
