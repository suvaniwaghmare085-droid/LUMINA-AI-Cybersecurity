"""Combines model and rule-based signals into an explainable risk score."""
def assess_risk(text_result=None, url_result=None):
    reasons = []
    components = []
    if text_result:
        # This is a risk indicator, not a calibrated probability of fraud.
        ml_score = round(text_result["scam_probability"] * 65)
        rule_score = min(35, len(text_result["reasons"]) * 9)
        text_score = min(100, ml_score + rule_score)
        components.append(text_score)
        reasons.extend(text_result["reasons"])
        if text_result["scam_probability"] >= 0.65:
            reasons.append("Machine-learning model found language similar to scam examples")
    if url_result:
        components.append(url_result["heuristic_score"])
        reasons.extend(url_result["signals"])

    score = max(components) if len(components) == 1 else (
        round(0.55 * components[0] + 0.45 * components[1]) if len(components) >= 2 else 0
    )
    score = max(0, min(100, score))
    level = "HIGH RISK" if score >= 70 else "SUSPICIOUS" if score >= 35 else "SAFE"
    if not reasons:
        reasons = ["No strong scam indicators were detected by the current checks"]
    return {
        "risk_score": score,
        "risk_level": level,
        "reasons": list(dict.fromkeys(reasons)),
        "disclaimer": "This is an educational risk assessment, not proof that content is safe or fraudulent. Do not share passwords, OTPs, PINs or payment details.",
    }
