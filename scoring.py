def generate_label(combined_score, attribution):
    """Map (combined_score, attribution) to the exact label text from
    planning.md -> ## Transparency Label Design. The uncertain variant
    explicitly invites an appeal.
    """
    confidence_pct = round(combined_score * 100)

    if attribution == "likely_ai":
        return (
            f"Likely AI-generated — our system detected strong AI-writing "
            f"patterns in this content (confidence: {confidence_pct}%)."
        )
    elif attribution == "likely_human":
        return (
            f"Likely human-written — our system found strong indicators of "
            f"human authorship in this content (confidence: {confidence_pct}%)."
        )
    else:
        return (
            f"Uncertain — we couldn't confidently determine whether this "
            f"content is AI-generated or human-written (confidence: "
            f"{confidence_pct}%). If you believe this is misclassified, you "
            f"can appeal."
        )


def score_confidence(llm_score, stylometric_score):
    """Combine the two signal scores per planning.md -> ## Uncertainty Representation.

    Returns (combined_score, attribution). Disagreement between signals dampens
    the combined score toward 0.5 (uncertain), and "likely_ai" additionally
    requires both signals to independently lean AI -- a high average alone
    isn't enough, since a false positive is worse than a false negative here.
    """
    combined_score = (llm_score + stylometric_score) / 2

    if abs(llm_score - stylometric_score) > 0.35:
        combined_score = 0.5 + (combined_score - 0.5) * 0.5

    if combined_score >= 0.7 and llm_score >= 0.55 and stylometric_score >= 0.55:
        attribution = "likely_ai"
    elif combined_score <= 0.3:
        attribution = "likely_human"
    else:
        attribution = "uncertain"

    return combined_score, attribution
