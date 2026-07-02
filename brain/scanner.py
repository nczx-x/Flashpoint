import re
from .heuristics.linguistic import AI_PHRASES
from .heuristics.structural import analyze_structure


def scan_answer(answer):
    body_raw = answer.get("body", "")
    body_text = re.sub(r"<[^<]+?>", "", body_raw).strip()
    reasons = []
    score = 0.0
    user_rep = answer.get("owner", {}).get("reputation", 0)

    if user_rep <= 1:
        score += 20
        reasons.append("New user (1 Rep)")
    elif user_rep < 100:
        score += 10
        reasons.append(f"Low rep user ({user_rep} Rep)")
    elif user_rep > 5000:
        score -= 20

    lower = body_text.lower()
    for phrase in AI_PHRASES:
        if phrase in lower:
            score += 18
            reasons.append(f"Contains AI phrase: '{phrase}'")

    if body_raw.count("**") > 8:
        score += 12
        reasons.append("High markdown density")
    if "<ul>" in body_raw and "<code>" not in body_raw:
        score += 10
        reasons.append("Bulleted list without code")

    structural_score, structural_reasons = analyze_structure(body_text)
    score += structural_score
    reasons.extend(structural_reasons)

    return int(max(0, min(100, round(score)))), reasons
