"""
ai_utils.py
------------
- Gemini-powered chatbot response generation
- Lightweight sentiment analysis (VADER — runs locally, no extra API cost)
- Crisis-keyword detection with resource surfacing
"""

import os
from google import genai
from google.genai import types
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ---------------------------------------------------------------------------
# Gemini setup
# ---------------------------------------------------------------------------
# Model name kept as a variable so it's easy to swap when Google updates
# their lineup. "gemini-flash-latest" auto-points to the newest stable Flash
# model, so you shouldn't need to touch this even after future releases.
GEMINI_MODEL_NAME = "gemini-flash-latest"

SYSTEM_INSTRUCTION = """You are a supportive, empathetic mental health companion chatbot
inside an app called MindCare AI. Your role:
- Listen actively and validate the user's feelings without judgment.
- Ask gentle, open-ended follow-up questions.
- Offer simple, evidence-informed coping strategies (breathing exercises,
  grounding techniques, journaling prompts, gentle reframes) when appropriate.
- NEVER diagnose any mental health condition.
- NEVER give medical, psychiatric, or medication advice.
- If the user expresses thoughts of self-harm, suicide, or being in crisis,
  respond with warmth, take it seriously, and gently encourage them to reach
  out to a crisis helpline or a trusted person/professional right away.
- Keep responses conversational and reasonably concise (3-6 sentences), not
  clinical or robotic.
- You are a supportive companion, not a replacement for a licensed therapist.
"""

_client = None


def configure_gemini(api_key: str):
    """Call once at app startup with the user-provided API key."""
    global _client
    _client = genai.Client(api_key=api_key)


def get_chat_response(conversation_history: list, user_message: str) -> str:
    """
    conversation_history: list of dicts [{"role": "user"/"model", "message": "..."}]
    Returns the model's text reply.
    """
    if _client is None:
        return "⚠️ Gemini API key not configured. Please add it in the sidebar."

    # Build Gemini-format history (roles must be 'user' or 'model')
    gemini_history = []
    for turn in conversation_history:
        role = "model" if turn["role"] in ("assistant", "model") else "user"
        gemini_history.append(
            types.Content(role=role, parts=[types.Part(text=turn["message"])])
        )

    try:
        chat = _client.chats.create(
            model=GEMINI_MODEL_NAME,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
            history=gemini_history,
        )
        response = chat.send_message(user_message)
        return response.text
    except Exception as e:
        return f"⚠️ Sorry, I hit an error talking to Gemini: {e}"


# ---------------------------------------------------------------------------
# Sentiment analysis (local, via VADER — fast and free)
# ---------------------------------------------------------------------------
_analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text: str):
    """
    Returns (label, compound_score) where label is one of
    'positive', 'neutral', 'negative' and compound_score is in [-1, 1].
    """
    scores = _analyzer.polarity_scores(text)
    compound = scores["compound"]
    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    return label, compound


# ---------------------------------------------------------------------------
# Crisis detection
# ---------------------------------------------------------------------------
# Pattern-level list of common distress phrases. This is intentionally kept
# simple (substring matching) — for a production system you'd want a proper
# classifier, but this is enough to catch clear crisis language in a student
# project and trigger a resource prompt.
CRISIS_PATTERNS = [
    "kill myself", "end my life", "suicide", "suicidal",
    "want to die", "don't want to live", "better off dead",
    "hurt myself", "self harm", "self-harm", "no reason to live",
    "can't go on", "cant go on", "ending it all",
]

CRISIS_RESOURCES_MD = """
### 💛 You're not alone — please reach out

If you're in immediate danger, please contact local emergency services right away.

**India**
- KIRAN Mental Health Helpline: **1800-599-0019** (24/7, toll-free)
- iCall (TISS): **9152987821** (Mon–Sat, 8am–10pm)
- Vandrevala Foundation: **1860-2662-345** / **9999666555** (24/7)

**International**
- If outside India, search "[your country] suicide helpline" or visit
  https://findahelpline.com for a verified local helpline.

Talking to someone you trust — a friend, family member, or counselor — can
also help right now.
"""


def detect_crisis(text: str) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in CRISIS_PATTERNS)
