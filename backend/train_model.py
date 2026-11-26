"""Train the lightweight text classifier used by LUMINA."""
from pathlib import Path
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from nltk.tokenize import TweetTokenizer

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "dataset" / "scam_messages.csv"
MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "text_model.joblib"

def train():
    data = pd.read_csv(DATA).dropna(subset=["text", "label"])
    if data["label"].nunique() < 2:
        raise ValueError("Training data must contain both scam and legitimate labels.")
    model = Pipeline([
        ("tfidf", TfidfVectorizer(
            lowercase=True, stop_words="english", ngram_range=(1, 2),
            max_features=12000, sublinear_tf=True,
            tokenizer=TweetTokenizer().tokenize, token_pattern=None
        )),
        ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced"))
    ])
    model.fit(data["text"].astype(str), data["label"].astype(str))
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Trained on {len(data)} examples. Model saved to: {MODEL_PATH}")
    print("Dataset is a small educational starter dataset; expand and validate it before real-world use.")
    return model

if __name__ == "__main__":
    train()
