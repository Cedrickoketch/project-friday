"""
AI service abstraction.
Set AI_PROVIDER=ollama  → uses local Ollama (gemma:2b) — great for development.
Set AI_PROVIDER=gemini  → uses Google Gemini API (free tier) — great for production.
"""
import json
from django.conf import settings


SYSTEM_PROMPT = """You are Friday, a smart and concise AI personal assistant.
You help the user manage tasks, events, and information efficiently.
When the user asks you to create a task, respond with a JSON block like:
{"action": "create_task", "title": "...", "due_date": "YYYY-MM-DD or null", "priority": "low|medium|high"}
When the user asks to create a calendar event:
{"action": "create_event", "title": "...", "start": "ISO8601", "end": "ISO8601", "description": "..."}
For general conversation, respond naturally and helpfully. Keep responses concise.
"""


def chat(messages: list[dict], user_message: str) -> dict:
    """
    messages: list of {"role": "user"|"assistant", "content": "..."}
    Returns: {"reply": str, "action": dict|None}
    """
    provider = settings.AI_PROVIDER

    if provider == "gemini":
        return _gemini_chat(messages, user_message)
    return _ollama_chat(messages, user_message)


def _ollama_chat(messages: list[dict], user_message: str) -> dict:
    import requests

    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages,
            {"role": "user", "content": user_message},
        ],
        "stream": False,
    }
    resp = requests.post(
        f"{settings.OLLAMA_BASE_URL}/api/chat",
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    reply_text = resp.json()["message"]["content"]
    return _parse_reply(reply_text)


def _gemini_chat(messages: list[dict], user_message: str) -> dict:
    import google.generativeai as genai

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",  # free tier
        system_instruction=SYSTEM_PROMPT,
    )
    # Convert messages to Gemini format
    history = []
    for m in messages:
        role = "user" if m["role"] == "user" else "model"
        history.append({"role": role, "parts": [m["content"]]})

    chat_session = model.start_chat(history=history)
    response = chat_session.send_message(user_message)
    return _parse_reply(response.text)


def _parse_reply(text: str) -> dict:
    """Try to extract a structured action JSON from the reply."""
    action = None
    # Look for a JSON block inside the reply
    import re
    match = re.search(r"\{.*?\}", text, re.DOTALL)
    if match:
        try:
            action = json.loads(match.group())
            # Remove the JSON from the display text
            text = text[:match.start()].strip() + text[match.end():].strip()
        except json.JSONDecodeError:
            pass
    return {"reply": text.strip(), "action": action}
