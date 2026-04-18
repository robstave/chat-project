import os

import httpx
from langchain_core.tools import tool

from commands.stats import (
    AWS_API_KEY,
    AWS_API_URL,
    AWS_USER,
    extract_metric_ids,
)

_HEADERS = {"x-api-key": AWS_API_KEY} if AWS_API_KEY else {}


def _fetch_metric_ids(user: str) -> list[str]:
    """Fetch all available metric IDs for a user (sync)."""
    resp = httpx.get(f"{AWS_API_URL}/users/{user}/metrics", headers=_HEADERS)
    if resp.status_code == 200:
        return extract_metric_ids(resp.json())
    return []


def _fetch_events(user: str, metric_id: str) -> str:
    """Fetch recent events for a metric and format them as a readable string."""
    resp = httpx.get(
        f"{AWS_API_URL}/users/{user}/metrics/{metric_id}/events",
        headers=_HEADERS,
        params={"limit": 10},
    )
    if resp.status_code != 200:
        return f"Error fetching {metric_id}: {resp.status_code}"

    data = resp.json()
    raw = data.get("items", data) if isinstance(data, dict) else data
    rows = sorted(
        [i for i in raw if isinstance(i, dict)],
        key=lambda x: x.get("timestamp", ""),
        reverse=True,
    )
    if not rows:
        return f"No events found for {metric_id}."

    lines = [f"Recent events for {metric_id}:"]
    for item in rows[:10]:
        ts = item.get("timestamp", "")[:10]
        val = item.get("value", "")
        lines.append(f"  {ts}: {val}")
    return "\n".join(lines)


@tool
def lookup_stat(question: str) -> str:
    """Look up a personal health or account metric based on a natural-language question.

    Use this tool when the user asks about their personal stats, metrics,
    measurements, account balances, steps, weight, blood pressure, temperature,
    drinks, body dimensions, or any tracked data.

    The tool fetches the list of available metrics, picks the best match for
    the question, and returns the recent events.

    Args:
        question: The user's natural-language question, e.g.
                  "what are my latest weights?" or "how many steps yesterday?"
    """
    user = AWS_USER or "default"
    metric_ids = _fetch_metric_ids(user)
    if not metric_ids:
        return "No metrics available."

    # Build a simple prompt for matching — the outer LLM will see the metric
    # list and the question and can pick the best one.  But since this is a
    # tool, we do a lightweight keyword match here to avoid a nested LLM call.
    q = question.lower()
    best = _best_match(q, metric_ids)
    if not best:
        return (
            "Could not determine which metric you mean. "
            f"Available metrics: {', '.join(metric_ids)}"
        )

    return _fetch_events(user, best)


def _best_match(query: str, metric_ids: list[str]) -> str | None:
    """Return the metric_id that best matches the query, or None."""
    # Keyword map — maps common words to metric id substrings
    keyword_map = {
        "weight": "weight",
        "step": "steps",
        "walk": "steps",
        "blood": "blood-pressure",
        "bp": "blood-pressure",
        "pressure": "blood-pressure",
        "temp": "temp",
        "garage": "temp-garage",
        "drink": "drinks",
        "alcohol": "drinks",
        "body": "body-dimensions",
        "dimension": "body-dimensions",
        "waist": "body-dimensions",
        "fidelity": "fidelity",
        "schwab": "schwab",
        "401k": "401k",
        "comcast": "comcast",
        "compushare": "compushare",
        "account": "account",
        "balance": "account",
    }

    # First pass: keyword matching
    for keyword, fragment in keyword_map.items():
        if keyword in query:
            for mid in metric_ids:
                if fragment in mid:
                    return mid

    # Second pass: direct substring match against metric ids
    for mid in metric_ids:
        # Check if any part of the metric id appears in the query
        parts = mid.replace("-", " ").split()
        for part in parts:
            if len(part) > 2 and part in query:
                return mid

    return None
