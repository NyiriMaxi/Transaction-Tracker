# TransTracker — MBH Bank SMS fizetés követő

MacroDroid → Python API → ML kategorizáló → CSV

## Architektúra

```
Telefon (MacroDroid)
  └─ SMS trigger (MBH Bank)
       └─ HTTP POST → sms_receiver.py (Flask, port 5000)
                            │
                    sms_parser.py       ← regex: összeg + tárgy
                            │
                    categorizer.py      ← TF-IDF + Logistic Regression
                            │
                    data/transactions.csv
```

## Telepítés

```bash
pip install -r requirements.txt
python train.py          # modell betanítása
python sms_receiver.py   # API szerver indítása
```

## MacroDroid beállítás

1. **Trigger:** SMS érkezett → Feladó szűrő: `telefonszám` (de lehet akár más is, én esetemben telefonszám)
2. **Action:** HTTP POST
   - URL: `http://<PC_IP>:5000/sms`
   - Body: `{"name": "{sms_name}", "message": "{sms_message}"}`
   - Header: `Content-Type: application/json`

A telefonnak és a PC-nek ugyanazon a WiFi-n kell lennie.

## API végpontok

| Végpont | Metódus | Leírás |
|---------|---------|--------|
| `/sms` | POST | SMS fogadása MacroDroid-tól |
| `/transactions` | GET | Összes tranzakció JSON-ban |
| `/summary` | GET | Havi összesítő kategóriánként |
| `/label` | POST | Ismeretlen tárgy kézzel megcímkézése |

## ML modell továbbfejlesztése

Ha egy tranzakció `Ismeretlen` kategóriába kerül:

```bash
# Kézzel megcímkézés (hozzáadja a tanítóadathoz)
curl -X POST http://localhost:5000/label \
  -H "Content-Type: application/json" \
  -d '{"subject": "ISMERETLEN BOLT", "category": "Élelmiszer"}'

# Újratanítás
python train.py
```

Vagy közvetlenül szerkeszd a `data/training_data.csv`-t, majd futtasd a `train.py`-t.

## Fájlstruktúra

```
├── sms_receiver.py       # Flask API
├── sms_parser.py         # MBH SMS regex parser
├── categorizer.py        # ML modell
├── train.py              # Tanítás / újratanítás
├── generate_training_data.py  # Seed tanítóadat generáló
├── data/
│   ├── transactions.csv  # Rögzített tranzakciók
│   └── training_data.csv # ML tanítóadat (szerkeszthető)
└── model/
    └── classifier.pkl    # Mentett modell
```
