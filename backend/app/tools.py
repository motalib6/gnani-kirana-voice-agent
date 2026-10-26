"""Order tools — the actions the agent is allowed to take.

These are the tool definitions an LLM agent would call. In this demo
they are plain Python functions so every tool call is testable and
auditable. An LLM must never be allowed to invent a tool result:
search_product only returns shop products, calculate_total only adds
listed prices, and save_order only saves what was parsed + confirmed.

Tools:
  search_product(query) -> matching products, or [] if none
  calculate_total(items) -> total from listed prices only
  save_order(customer, items) -> order id (via order_store)
  handoff(reason) -> human-handoff message, no order saved
"""
from . import order_store
from .rag import retrieve


def search_product(query, price_list, knowledge_base):
    docs = retrieve(query, price_list, knowledge_base, top_k=5)
    return [d for d in docs if d["type"] == "product"]


def calculate_total(items):
    return round(sum(i["quantity"] * i["price_per_unit"] for i in items), 2)


def save_order_tool(customer_name, items):
    total = calculate_total(items)
    order_id = order_store.save_order(customer_name, items, total, status="pending")
    return {"order_id": order_id, "total": total, "status": "pending"}


def handoff(reason):
    return {
        "action": "handoff",
        "message": (
            "Ye order dukandar ko bhej diya gaya hai, wo khud confirm karenge. "
            f"Reason: {reason}"
        ),
    }
