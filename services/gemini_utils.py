import io
import json
import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


def _fallback(planner: str, data: dict) -> dict:
    budget = float(data.get("budget", 0))
    if planner == "home":
        allocations = {
            "Furniture & Tables": round(budget * 0.35, 2),
            "Lighting": round(budget * 0.20, 2),
            "Ceiling Fans": round(budget * 0.15, 2),
            "Decor": round(budget * 0.20, 2),
            "Reserve": round(budget * 0.10, 2),
        }
        return {
            "title": "Home Interior Recommendations",
            "summary": f"A {data.get('style','Modern')} {data.get('room_type','room')} plan within ₹{budget:,.0f}.",
            "allocation": allocations,
            "recommendations": [
                {"name": "Compact dining / accent table", "platform": "IKEA", "price": "₹6,000–₹12,000", "reason": "Balances function and available budget."},
                {"name": "LED ceiling lights", "platform": "Amazon", "price": "₹1,500–₹4,000", "reason": "Affordable lighting with multiple style choices."},
                {"name": "Energy-efficient ceiling fan", "platform": "Amazon", "price": "₹2,500–₹5,000", "reason": "Keeps the room practical without overspending."},
                {"name": "Wall decor set", "platform": "Amazon / IKEA", "price": "₹1,000–₹3,000", "reason": "Adds visual character while preserving the reserve."},
            ],
        }
    if planner == "party":
        allocations = {
            "Catering": round(budget * 0.45, 2),
            "Decoration": round(budget * 0.20, 2),
            "Entertainment": round(budget * 0.15, 2),
            "Venue": round(budget * 0.15, 2),
            "Reserve": round(budget * 0.05, 2),
        }
        return {
            "title": "Party Budget Recommendations",
            "summary": f"A {data.get('event_type','party')} plan for {data.get('guests',0)} guests within ₹{budget:,.0f}.",
            "allocation": allocations,
            "recommendations": [
                {"name": "Catering package", "platform": "Swiggy / Zomato", "price": f"Up to ₹{allocations['Catering']:,.0f}", "reason": "Largest share is reserved for food."},
                {"name": "Venue option", "platform": "OYO / Local venue", "price": f"Up to ₹{allocations['Venue']:,.0f}", "reason": "Keeps venue spending controlled."},
                {"name": "Decoration package", "platform": "Local vendors", "price": f"Up to ₹{allocations['Decoration']:,.0f}", "reason": "Supports the selected event style."},
                {"name": "Entertainment", "platform": "Local vendors", "price": f"Up to ₹{allocations['Entertainment']:,.0f}", "reason": "Leaves room for music or activities."},
            ],
        }
    return {
        "title": "Jewelry Budget Recommendations",
        "summary": f"Jewelry ideas for a {data.get('occasion','special occasion')} with a {data.get('style','classic')} style.",
        "allocation": {"Main Piece": round(budget * .55, 2), "Earrings": round(budget * .25, 2), "Accessories": round(budget * .10, 2), "Reserve": round(budget * .10, 2)},
        "recommendations": [
            {"name": "Statement necklace", "platform": "Amazon", "price": "₹2,000–₹6,000", "reason": "Works as the main focal piece."},
            {"name": "Matching earrings", "platform": "Flipkart", "price": "₹1,000–₹3,000", "reason": "Complements the necklace and occasion."},
            {"name": "Minimal bracelet", "platform": "Amazon", "price": "₹500–₹1,500", "reason": "Adds a coordinated finishing detail."},
        ],
    }


def get_recommendations(planner: str, data: dict, image_bytes: Optional[bytes], mime_type: Optional[str]) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return _fallback(planner, data)

    try:
        from google import genai
        from PIL import Image

        client = genai.Client(api_key=api_key)
        domain = {
            "home": "home interior planning",
            "party": "party/event budget planning",
            "jewelry": "jewelry recommendation for an occasion",
        }.get(planner, planner)

        prompt = f"""
You are PocketSmart AI, a budget-aware recommendation assistant.
Task: {domain}
User data:
{json.dumps(data, indent=2)}

Return ONLY valid JSON with exactly these keys:
title: string
summary: string
allocation: object mapping category names to numeric INR amounts
recommendations: array of 4 objects, each with:
name, platform, price, reason

Rules:
- Stay within the user's total budget.
- Make it clear that platform names are suggested sources, not live inventory.
- Do not invent exact live product availability.
- Use Indian Rupees (₹).
- Keep suggestions practical and concise.
"""
        contents = [prompt]
        if image_bytes and mime_type and mime_type.startswith("image/"):
            image = Image.open(io.BytesIO(image_bytes))
            contents.append(image)
            contents.append("Use the uploaded outfit image only to discuss broad color/style coordination.")

        response = client.models.generate_content(model=MODEL, contents=contents)
        text = (response.text or "").strip()
        if text.startswith("```"):
            text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        if not isinstance(result.get("recommendations"), list):
            raise ValueError("Invalid recommendation structure")
        return result
    except Exception:
        return _fallback(planner, data)
