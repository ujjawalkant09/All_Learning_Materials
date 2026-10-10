"""Milestone 8 · Command-line app  (revise: steps 08, 11, 14)

Run from the folder that contains ``expense_assistant/``::

    python -m expense_assistant.cli                # agent mode: all tools, approvals, budget alerts
    python -m expense_assistant.cli --mode graph   # LangGraph router mode
    python -m expense_assistant.cli --seed         # add sample expenses first

Check: pytest tests/test_m8_cli.py
"""

import argparse
import uuid

from dotenv import load_dotenv
from langchain.messages import AIMessage, HumanMessage  # noqa: F401
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command  # noqa: F401

from . import db


def new_ai_replies(messages: list) -> list[str]:
    """Text of the AI messages produced after the last human message, in order.

    Skip AI messages with empty content (those are tool-call requests).

    TODO (M8): walk ``messages`` backwards until you hit a HumanMessage.
    """
    raise NotImplementedError("M8: implement new_ai_replies")


def resolve_interrupts(agent, result: dict, config: dict, decide=input) -> dict:
    """Ask the human about every paused tool call until nothing is pending.

    TODO (M8): while "__interrupt__" in result:
      - for each interrupt, for each ``action`` in ``interrupt.value["action_requests"]``:
        ask ``decide(f"Approve {action['name']}({action['args']})? [y/n] ")``
        → ``{"type": "approve"}`` or ``{"type": "reject", "message": "..."}``
      - ``result = agent.invoke(Command(resume={"decisions": decisions}), config)``
      return the final result.
    """
    raise NotImplementedError("M8: implement resolve_interrupts")


def chat_loop(mode: str, thread_id: str) -> None:
    """Read user input until 'exit' and print the assistant's replies. (Given.)"""
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
    """Parse arguments, load .env, prepare the DB and start chatting. (Given.)"""
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
