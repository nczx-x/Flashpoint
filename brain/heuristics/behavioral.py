def analyze_behavior(answer):
    score = 0
    reasons = []
    user_rep = answer.get("owner", {}).get("reputation", 0)
    if user_rep <= 1:
        score += 20
        reasons.append("New user reputation")
    elif 1 < user_rep < 100:
        score += 10
        reasons.append("Low reputation user")

    if answer.get("score", 0) <= 0:
        score += 8
        reasons.append("Low-voted answer")

    if answer.get("creation_date") and answer.get("last_activity_date"):
        if answer["last_activity_date"] - answer["creation_date"] < 600:
            score += 6
            reasons.append("Rapid activity on answer")

    return score, reasons
