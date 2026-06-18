"""Kategorizáló tesztek."""

import os
import tempfile

import pandas as pd
import pytest

from categorizer import normalize, train, predict, CONFIDENCE_THRESHOLD


def test_normalize_lowercase():
    assert normalize("LIDL HUNGARY") == "lidl hungary"


def test_normalize_removes_accents():
    assert normalize("Élelmiszer") == "elelmiszer"


def test_normalize_removes_special_chars():
    result = normalize("BOLT-2024/KFT.")
    assert "/" not in result
    assert "-" not in result
    assert "." not in result


def test_normalize_collapses_whitespace():
    assert normalize("  LIDL   HUNGARY  ") == "lidl hungary"


@pytest.fixture
def trained_model(tmp_path):
    """Minimális modell ideiglenes fájlokkal."""
    data = []
    categories = ["Élelmiszer", "Közlekedés", "Szórakozás"]
    examples = {
        "Élelmiszer": ["LIDL", "TESCO", "SPAR", "ALDI", "CBA"],
        "Közlekedés": ["BKK", "MAV", "VOLANBUSZ", "PARKING", "BENZIN"],
        "Szórakozás": ["MOZI", "NETFLIX", "STEAM", "JEGY", "CONCERT"],
    }
    for cat, subjects in examples.items():
        for s in subjects:
            data.append({"subject": s, "category": cat})

    csv_path = tmp_path / "training_data.csv"
    model_path = tmp_path / "classifier.pkl"
    pd.DataFrame(data).to_csv(csv_path, index=False)
    train(training_data_path=str(csv_path), model_path=str(model_path))
    return str(model_path)


def test_predict_known_category(trained_model):
    category, confidence = predict("LIDL HUNGARY KFT", model_path=trained_model)
    assert category == "Élelmiszer"
    assert confidence >= CONFIDENCE_THRESHOLD


def test_predict_returns_ismeretlen_for_garbage(trained_model):
    import categorizer
    categorizer._model = None
    category, confidence = predict("XYZQWERTY123UNKNOWN", model_path=trained_model)
    assert isinstance(category, str)
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0


def test_predict_confidence_is_float(trained_model):
    _, confidence = predict("TESCO", model_path=trained_model)
    assert isinstance(confidence, float)
    assert 0.0 <= confidence <= 1.0
