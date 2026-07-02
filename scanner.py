import re
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = None
AI_PHRASES = [
    "certainly!",
    "here are a few",
    "it's important to note",
    "in conclusion",
    "to summarize",
    "i hope this helps",
    "let me know if you have",
    "as an ai language model",
    "based on my training",
]

def scan_answer(answer):
    body_raw = answer.get("body", "")
    body_text = re.sub("<[^<]+?>", "", body_raw).strip()
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
            reasons.append(f"Contains AI-like phrase: '{phrase}'")
    if body_raw.count("**") > 8:
        score += 12
        reasons.append("Very high bold/markdown density")
    if "<ul>" in body_raw and "<code>" not in body_raw:
        score += 10
        reasons.append("Bulleted lists with no code/examples")
    try:
        if nlp is not None and body_text:
            doc = nlp(body_text)
            tokens = [t for t in doc if not t.is_space]
            token_count = max(1, len(tokens))
            sents = list(doc.sents)
            sent_count = max(1, len(sents))
            avg_sent_len = sum(len([t for t in s if not t.is_space]) for s in sents) / sent_count
            types = {t.lemma_.lower() for t in tokens if t.is_alpha}
            ttr = len(types) / token_count
            pos_counts = {}
            for t in tokens:
                pos_counts[t.pos_] = pos_counts.get(t.pos_, 0) + 1
            noun_ratio = pos_counts.get("NOUN", 0) / token_count
            verb_ratio = pos_counts.get("VERB", 0) / token_count
            pron_ratio = pos_counts.get("PRON", 0) / token_count
            ent_count = len(list(doc.ents))
            first_person = sum(1 for t in tokens if t.lower_ in ("i", "we", "me", "us", "my", "our"))
            first_person_ratio = first_person / token_count
            passive = any(t.dep_ in ("nsubjpass", "auxpass") for t in doc)
            if avg_sent_len > 22:
                score += 12
                reasons.append(f"Long sentences (avg {avg_sent_len:.1f} tokens)")
            if ttr < 0.25 and token_count > 60:
                score += 12
                reasons.append(f"Low lexical diversity (TTR {ttr:.2f})")
            if pron_ratio < 0.03 and token_count > 40:
                score += 8
                reasons.append(f"Very low pronoun ratio ({pron_ratio:.2f})")
            if first_person_ratio > 0.06:
                score -= 6
                reasons.append("Contains first-person phrasing (human-like)")
            if ent_count < max(1, token_count // 200):
                score += 6
                reasons.append(f"Few named entities ({ent_count})")
            if passive:
                score += 4
                reasons.append("Passive voice detected")
            if noun_ratio > 0.45 and verb_ratio < 0.12 and token_count > 40:
                score += 10
                reasons.append(f"Noun-heavy, low-verbs (noun_ratio {noun_ratio:.2f})")
    except Exception:
        pass
    return int(max(0, min(100, round(score)))), reasons
