"""Text classification and human-readable signal extraction."""
from pathlib import Path
import re
import joblib
from train_model import MODEL_PATH, train

URL_RE = re.compile(r"https?://[^\s<>()]+|www\.[^\s<>()]+", re.IGNORECASE)

SIGNAL_PATTERNS = [
    ("Urgent or threatening language", r"\b(urgent|immediately|final warning|today|now|expire|blocked|suspend|deactivated|disconnected|arrest)\b"),
    ("Prize, reward or lottery language", r"\b(won|winner|prize|lottery|giveaway|reward|free gift|claim)\b"),
    ("Requests for sensitive information", r"\b(otp|one.time.password|upi pin|pin|password|cvv|card number|bank details|recovery phrase)\b"),
    ("Payment or fee pressure", r"\b(pay|payment|fee|fine|registration charge|joining fee|redelivery charge)\b"),
    ("Unrealistic income or guaranteed returns", r"\b(guaranteed returns|double your money|huge money|risk.free profit)\b"),
    ("Account verification pressure", r"\b(verify|kyc|confirm your account|update details|account access)\b"),
]

def load_model():
    if not MODEL_PATH.exists():
        train()
    return joblib.load(MODEL_PATH)

def extract_text_signals(text):
    reasons = []
    lowered = text.lower()
    for label, pattern in SIGNAL_PATTERNS:
        if re.search(pattern, lowered, flags=re.IGNORECASE):
            reasons.append(label)
    if URL_RE.search(text):
        reasons.append("Message contains a web link")
    if re.search(r"\b(otp|upi pin|cvv|password)\b", lowered) and re.search(r"\b(send|share|provide|enter|tell)\b", lowered):
        reasons.append("Appears to ask the recipient to disclose a secret credential")
    return list(dict.fromkeys(reasons))

def analyze_text(text, model=None):
    cleaned = re.sub(r"\s+", " ", str(text)).strip()
    if not cleaned:
        raise ValueError("Please enter a message to analyze.")
    model = model or load_model()
    probabilities = model.predict_proba([cleaned])[0]
    classes = list(model.classes_)
    scam_probability = float(probabilities[classes.index("scam")]) if "scam" in classes else 0.0
    reasons = extract_text_signals(cleaned)
    return {
        "prediction": "scam" if scam_probability >= 0.5 else "legitimate",
        "scam_probability": round(scam_probability, 4),
        "reasons": reasons,
        "contains_url": bool(URL_RE.search(cleaned)),
    }
