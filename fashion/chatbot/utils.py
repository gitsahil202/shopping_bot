import json 
from openai import OpenAI
from dotenv import load_dotenv
from database.models import Product
import os

load_dotenv()
client=OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_chat_history(request):
    return request.session.get("chat_history", [])

def update_chat_history(request, query, bot_reply):
    chat_history = request.session.get("chat_history", [])
    chat_history.append({"role": "user", "content": query})
    chat_history.append({"role": "assistant", "content": bot_reply})
    request.session["chat_history"] = chat_history
    request.session.modified = True

def get_bot_reply(chat_history, query):
    system_prompt = """
    You are a shopping assistant for a fashion store.

    Your job:
    - Help users find products by narrowing down their preferences (category, sub_category, color, size).
    - If the user query is vague, ask ONE clarifying question.
    - If enough information is available, return ONLY a JSON object with filters (no extra text).

    ### Rules for JSON output:
    1. The JSON must only include keys with known values.
    2. Do not include a key if its value is unknown or unspecified.
    3. The JSON format is:
    {
        "category": "...",
        "sub_category": "...",
        "color": "...",
        "size": "..."
    }
    4. Never include values outside the allowed choices.

    ### Allowed values:
    - category: ["clothes", "footwear", "accessories"]
    - sub_category (depends on category):
    - clothes: ["tshirts", "shirts", "jeans", "trousers"]
    - footwear: ["formal_shoes", "sneakers", "flip_flops"]
    - accessories: ["watches", "rings", "pendants"]
    - color: ["red", "green", "blue", "yellow", "black", "brown", "gold", "silver"]
    - size: ["S", "M", "L", "XL", "XXL"]

    ### Additional rules:
    - If user gives sub_category without category, infer the category.
    Example: "I want a watch" → {"category": "accessories", "sub_category": "watches"}.
    - If user says "all sizes" or "any size", do not include "size" in JSON.
    - If unsure about a value, omit that key entirely.
    - Respond ONLY in one of these two ways:
    1. Clarifying question (natural language).
    2. JSON object (filters).

    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            *chat_history,
            {"role": "user", "content": query}   
        ],
        temperature=0.2
    )
    answer=response.choices[0].message.content.strip()
    return answer

def extract_filters(bot_reply: str) -> dict:
    try:
        return json.loads(bot_reply)
    except json.JSONDecodeError:
        return {}


def query_products(filters):
    if not filters:
        return []
     
    qs = Product.objects.filter(stock__gt=0)

    if "category" in filters and filters["category"]:
        qs = qs.filter(category__icontains=filters["category"])
    if "sub_category" in filters and filters["sub_category"]:
        qs = qs.filter(sub_category__icontains=filters["sub_category"])
    if "color" in filters and filters["color"]:
        qs = qs.filter(color__icontains=filters["color"])
    if "size" in filters and filters["size"]:
        qs = qs.filter(size__icontains=filters["size"])

    return [
        {
            "name": p.title,
            "price": str(p.price),
            "type": p.sub_category,
            "image": p.image.url if p.image else None
        }
        for p in qs
    ]