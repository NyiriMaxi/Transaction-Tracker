"""
ML alapú tranzakció kategorizáló.

Pipeline:
  subject szöveg
    → szöveg normalizálás
    → TF-IDF (karakter n-gram, toleráns az elgépeléssel szemben)
    → Logistic Regression
    → kategória + konfidencia

Ha a konfidencia alacsony (< CONFIDENCE_THRESHOLD), az ismeretlen
kategóriába kerül és kézzel lehet megcímkézni a training_data.csv-ben,
majd újra kell tanítani a modellt.
"""

import os
import pickle
import re
import unicodedata

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

TRAINING_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "training_data.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "classifier.pkl")
CONFIDENCE_THRESHOLD = 0.12


def normalize(text: str) -> str:
    """Kisbetűsítés, ékezetek eltávolítása, csak alfanumerikus karakterek."""
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def build_pipeline() -> Pipeline:
    return Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                analyzer="char_wb",   # karakter n-gram: toleráns elírásokra
                ngram_range=(2, 4),
                min_df=1,
                max_features=10_000,
            ),
        ),
        (
            "clf",
            LogisticRegression(
                max_iter=1000,
                C=1.0,
                class_weight="balanced",  # kiegyensúlyozza a ritka kategóriákat
            ),
        ),
    ])


def train(training_data_path: str = TRAINING_DATA_PATH, model_path: str = MODEL_PATH) -> None:
    df = pd.read_csv(training_data_path)
    df["subject_norm"] = df["subject"].apply(normalize)

    X = df["subject_norm"].tolist()
    y = df["category"].tolist()

    if len(set(y)) < 2:
        raise ValueError("Legalább 2 különböző kategória szükséges a tanításhoz.")

    from collections import Counter
    counts = Counter(y)
    can_stratify = len(X) > 20 and min(counts.values()) >= 2
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y if can_stratify else None
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    print("=== Kiértékelés (teszt adatokon) ===")
    print(classification_report(y_test, y_pred, zero_division=0))

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(pipeline, f)
    print(f"Modell mentve: {model_path}")


def load_model(model_path: str = MODEL_PATH) -> Pipeline:
    if not os.path.exists(model_path):
        print("Nincs mentett modell, tanítás most...")
        train(model_path=model_path)
    with open(model_path, "rb") as f:
        return pickle.load(f)


_model: Pipeline | None = None


def predict(subject: str, model_path: str = MODEL_PATH) -> tuple[str, float]:
    """
    Visszaadja a (kategória, konfidencia) párt.
    Ha a konfidencia < CONFIDENCE_THRESHOLD, kategória = "Ismeretlen".
    """
    global _model
    if _model is None:
        _model = load_model(model_path)

    norm = normalize(subject)
    proba = _model.predict_proba([norm])[0]
    best_idx = int(np.argmax(proba))
    confidence = float(proba[best_idx])
    category = _model.classes_[best_idx]

    if confidence < CONFIDENCE_THRESHOLD:
        return "Ismeretlen", confidence

    return category, confidence


def add_training_example(subject: str, category: str, path: str = TRAINING_DATA_PATH) -> None:
    """Új tanítóadatot fűz a CSV-hez (kézzel javított példák)."""
    row = pd.DataFrame([{"subject": subject, "category": category}])
    row.to_csv(path, mode="a", header=False, index=False)
    print(f"Hozzáadva: '{subject}' → '{category}'")
    print("Futtasd a train.py-t az újratanításhoz.")
