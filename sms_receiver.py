"""
Flask API szerver — MacroDroid ide POST-olja az SMS-eket.

MacroDroid beállítás:
  Trigger:  SMS érkezett (feladó szűrő: MBH vagy a bank száma)
  Action:   HTTP POST
    URL:    http://<PC_IP>:5000/sms
    Body:   {"sender": "{sms_sender}", "body": "{sms_body}"}
    Header: Content-Type: application/json
"""

import csv
import os
from datetime import datetime

from flask import Flask, jsonify, request

from categorizer import predict, add_training_example
from sms_parser import parse_sms

app = Flask(__name__)

TRANSACTIONS_CSV = os.path.join(os.path.dirname(__file__), "data", "transactions.csv")
CSV_HEADERS = ["dátum", "összeg", "tárgy", "kategória", "konfidencia", "típus", "nyers_sms"]


def ensure_csv():
    if not os.path.exists(TRANSACTIONS_CSV):
        os.makedirs(os.path.dirname(TRANSACTIONS_CSV), exist_ok=True)
        with open(TRANSACTIONS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)


def save_transaction(date: str, amount: float, subject: str,
                     category: str, confidence: float,
                     tx_type: str, raw_sms: str) -> None:
    with open(TRANSACTIONS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([date, amount, subject, category, f"{confidence:.2f}", tx_type, raw_sms])


@app.route("/sms", methods=["POST"])
def receive_sms():
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "Hiányzó 'message' mező"}), 400

    sms_body = data["message"]
    transaction = parse_sms(sms_body)

    if transaction is None:
        return jsonify({"status": "skip", "reason": "Nem banki SMS (nincs összeg)"}), 200

    category, confidence = predict(transaction.subject)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sms_date = transaction.date or now

    save_transaction(
        date=sms_date,
        amount=transaction.amount,
        subject=transaction.subject,
        category=category,
        confidence=confidence,
        tx_type="POS",
        raw_sms=transaction.raw_sms,
    )

    result = {
        "status": "ok",
        "date": sms_date,
        "amount": transaction.amount,
        "subject": transaction.subject,
        "category": category,
        "confidence": round(confidence, 3),
    }
    print(f"[{sms_date}] {transaction.amount} Ft | {transaction.subject} -> {category} ({confidence:.0%})")
    return jsonify(result), 200


@app.route("/label", methods=["POST"])
def label_transaction():
    """
    Kézzel megcímkéz egy ismeretlen tárgyat, és hozzáadja a tanítóadathoz.
    Body: {"subject": "...", "category": "..."}
    """
    data = request.get_json(silent=True)
    if not data or "subject" not in data or "category" not in data:
        return jsonify({"error": "Hiányzó 'subject' vagy 'category'"}), 400

    add_training_example(data["subject"], data["category"])
    return jsonify({"status": "ok", "message": "Mentve. Futtasd a train.py-t!"}), 200


@app.route("/transactions", methods=["GET"])
def get_transactions():
    """Visszaadja az összes tranzakciót JSON-ban."""
    if not os.path.exists(TRANSACTIONS_CSV):
        return jsonify([]), 200
    rows = []
    with open(TRANSACTIONS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return jsonify(rows), 200


@app.route("/summary", methods=["GET"])
def get_summary():
    """Kategóriánkénti összesítő az aktuális hónapra."""
    if not os.path.exists(TRANSACTIONS_CSV):
        return jsonify({}), 200

    current_month = datetime.now().strftime("%Y-%m")
    totals: dict[str, float] = {}

    with open(TRANSACTIONS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["dátum"].startswith(current_month):
                cat = row["kategória"]
                totals[cat] = totals.get(cat, 0.0) + float(row["összeg"])

    return jsonify(totals), 200


if __name__ == "__main__":
    ensure_csv()
    print("TransTracker API indul... http://0.0.0.0:5000")
    print("MacroDroid célpont: http://<PC_IP>:5000/sms")
    app.run(host="0.0.0.0", port=5000, debug=True)
