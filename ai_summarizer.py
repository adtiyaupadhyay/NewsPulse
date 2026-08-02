"""
ai_summarizer.py
------------------
This is the AI layer. For each article, we ask an LLM to return
a summary + category + sentiment — but critically, we FORCE it to
respond in JSON, not free text.

Why JSON mode instead of just asking "summarize this" in plain English?
  - Free text output is unpredictable: sometimes it gives you a
    paragraph, sometimes bullet points, sometimes it adds commentary
    you didn't ask for ("Sure! Here's a summary:"). You'd then need
    fragile regex/string-parsing to extract just the summary — and
    that breaks the moment the model phrases something slightly
    differently.
  - JSON output is structured and predictable: we ask for exact
    keys (summary, category, sentiment), so python's json.loads()
    can parse it directly, every time, no guessing.

Why FEW-SHOT examples in the prompt (showing 2 example inputs/outputs
before the real one)?
  - It anchors the model's behavior. Without examples, the model
    might write a 5-line summary sometimes and a 1-line summary
    other times, or invent category names inconsistently ("Tech"
    vs "Technology" vs "tech news"). Examples lock in the exact
    format and vocabulary we want, every single time.
"""

import os
import json
from groq import Groq

def get_api_key():
    """Try Streamlit secrets first (for deployed app), fall back to
    environment variable (for local development)."""
    try:
        import streamlit as st
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.environ.get("GROQ_API_KEY")

client = Groq(api_key=get_api_key())

# These few-shot examples are shown to the model as part of the prompt,
# so it learns the EXACT shape of output we expect.
FEW_SHOT_EXAMPLES = """
Example 1:
Title: "OpenAI releases new reasoning model with improved coding benchmarks"
Output: {"summary": "OpenAI launched a new model focused on reasoning tasks, showing gains on coding benchmarks over its predecessor.", "category": "AI", "sentiment": "positive"}

Example 2:
Title: "Startup lays off 200 employees amid funding crunch"
Output: {"summary": "A startup cut 200 jobs as it struggles to secure new funding in a tightening investment climate.", "category": "Startups", "sentiment": "negative"}
"""

CATEGORIES = ["AI", "Startups", "Programming", "Business", "Policy", "Other"]


def summarize_article(title: str) -> dict:
    """Sends one article title to the LLM and returns a dict with
    summary, category, sentiment. Falls back to a safe default if
    anything goes wrong (bad JSON, API failure, etc.) — we NEVER
    want one bad article to crash the whole pipeline."""

    prompt = f"""You are a news classification assistant. Given an article
title, respond with ONLY a JSON object (no other text, no markdown
formatting, no explanation) with exactly these keys:
- "summary": a 1-2 line summary based on the title
- "category": one of {CATEGORIES}
- "sentiment": one of ["positive", "negative", "neutral"]

Here are examples of the exact format expected:
{FEW_SHOT_EXAMPLES}

Now do the same for this article:
Title: "{title}"
Output:"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,   # low temperature = more consistent, less "creative" output
            max_tokens=200,
        )
        raw_text = response.choices[0].message.content.strip()

        # Sometimes models wrap JSON in ```json ... ``` even when told not to.
        # Strip that defensively rather than trusting the instruction blindly.
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`").replace("json", "", 1).strip()

        parsed = json.loads(raw_text)

        # Validate the shape before trusting it — don't just assume the
        # model followed instructions perfectly every time.
        if not all(k in parsed for k in ("summary", "category", "sentiment")):
            raise ValueError("Missing expected keys in AI response")

        return parsed

    except (json.JSONDecodeError, ValueError, Exception) as e:
        print(f"  ⚠️  AI summarization failed for '{title[:50]}...': {e}")
        return {
            "summary": "Summary unavailable.",
            "category": "Other",
            "sentiment": "neutral",
        }


if __name__ == "__main__":
    # Quick manual test with a couple of real-sounding titles
    test_titles = [
        "New Python framework promises 10x faster web development",
        "Tech layoffs continue as company cuts 15% of workforce",
    ]
    for t in test_titles:
        result = summarize_article(t)
        print(f"\nTitle: {t}")
        print(f"Result: {result}")