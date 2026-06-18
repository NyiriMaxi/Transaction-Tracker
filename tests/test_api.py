"""Flask API végpont tesztek."""

import json
import pytest

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sms_receiver import app as flask_app
from database import TransactionDB


@pytest.fixture
def client(tmp_path):
    db_path = str(tmp_path / "test.db")
    import sms_receiver
    sms_receiver.db = TransactionDB(db_path=db_path)
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


def test_index_returns_200(client):
    res = client.get("/")
    assert res.status_code == 200


def test_sms_missing_message_returns_400(client):
    res = client.post("/sms", json={"sender": "MBH"})
    assert res.status_code == 400


def test_sms_non_bank_message_returns_skip(client):
    res = client.post("/sms", json={"message": "Kedves ügyfelünk, akciós ajánlat!"})
    assert res.status_code == 200
    assert res.get_json()["status"] == "skip"


def test_sms_valid_returns_ok(client):
    sms = (
        "Mastercard Standard POS tranzakció 5490Ft időpont: 2024.01.15 14:23:45 "
        "E: 45320 Ft Hely: LIDL HUNGARY KFT"
    )
    res = client.post("/sms", json={"message": sms})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert data["amount"] == 5490.0
    assert data["subject"] == "LIDL HUNGARY KFT"


def test_transactions_returns_json(client):
    res = client.get("/transactions")
    assert res.status_code == 200
    assert isinstance(res.get_json(), dict)


def test_summary_returns_json(client):
    res = client.get("/summary?month=2024-01")
    assert res.status_code == 200
    assert isinstance(res.get_json(), dict)


def test_label_missing_fields_returns_400(client):
    res = client.post("/label", json={"subject": "LIDL"})
    assert res.status_code == 400


def test_label_valid_returns_ok(client):
    res = client.post("/label", json={"subject": "LIDL HUNGARY", "category": "Élelmiszer"})
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"
