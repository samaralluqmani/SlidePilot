import re

from models.deck import Deck


WEIGHTS = {
    "technology": {
        "artificial intelligence": 3,
        "machine learning": 3,
        "software": 2,
        "automation": 2,
        "cloud": 2,
        "cybersecurity": 3,
        "api": 2,
        "platform": 1,
        "technology": 2,
        "digital": 1,
        "data pipeline": 2,
    },
    "business": {
        "business": 2,
        "market": 2,
        "sales": 3,
        "revenue": 3,
        "customer": 2,
        "strategy": 2,
        "growth": 2,
        "financial": 3,
        "operations": 2,
        "investment": 3,
        "profit": 3,
    },
    "academic": {
        "research": 3,
        "study": 2,
        "academic": 3,
        "university": 3,
        "methodology": 3,
        "literature review": 3,
        "experiment": 2,
        "hypothesis": 3,
        "findings": 2,
        "references": 2,
        "researcher": 2,
    },
}


def _score(text: str, terms: dict[str, int]) -> int:
    score = 0
    for term, weight in terms.items():
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, text, flags=re.IGNORECASE):
            score += weight
    return score


def resolve_theme(deck: Deck, source_text: str, override: str | None = None) -> Deck:
    if override in {"technology", "business", "academic"}:
        deck.theme = override
        return deck

    scores = {name: _score(source_text, terms) for name, terms in WEIGHTS.items()}
    strongest = max(scores, key=scores.get)
    ai_theme = deck.theme

    # Trust the structured planner unless the document evidence is clearly stronger elsewhere.
    if strongest != ai_theme and scores[strongest] >= scores.get(ai_theme, 0) + 4 and scores[strongest] >= 6:
        deck.theme = strongest

    return deck
