# TransTracker — SMS fizetés követő

MacroDroid → Python Flask API → ML kategorizáló → SQLite → Web dashboard

## Architektúra

```
Telefon (MacroDroid)
  └─ SMS trigger
       └─ HTTP POST → sms_receiver.py (Flask, port 5000)
                            │
                    sms_parser.py       ← regex: összeg + tárgy
                            │
                    categorizer.py      ← TF-IDF + Logistic Regression
                            │
                    data/transactions.db (SQLite)
                            │
                    templates/index.html ← Chart.js dashboard
```

## Funkciók

- **SMS feldolgozás** - Banki tranzakciós SMS-ek automatikus fogadása MacroDroid-on keresztül
- **ML kategorizálás** - TF-IDF + Logistic Regression modell, karakter n-gram alapú
- **Web dashboard** - havi kördiagram, tranzakcióslista, hónapnavigáció
- **Docker támogatás** - konténerizált futtatás
- **CI** - GitHub Actions automatikusan futtatja a teszteket minden push-ra

## Dashboard

*(screenshot hamarosan)*

## Telepítés

```bash
pip install -r requirements.txt
python train.py
python sms_receiver.py
```

### Docker

```bash
docker compose build
docker compose up
```

## MacroDroid beállítás

1. **Trigger:** SMS érkezett → Feladó szűrő: `telefonszám`
2. **Action:** HTTP POST
   - URL: `http://<PC_IP>:5000/sms`
   - Body: `{"name": "{sms_name}", "message": "{sms_message}"}`
   - Header: `Content-Type: application/json`

Más hálózatról: Tailscale segítségével elérhető a szerver VPN-en keresztül.

## API végpontok

| Végpont | Metódus | Leírás |
|---------|---------|--------|
| `/` | GET | Web dashboard |
| `/sms` | POST | SMS fogadása MacroDroid-tól |
| `/transactions` | GET | Összes tranzakció JSON-ban |
| `/summary?month=YYYY-MM` | GET | Havi összesítő kategóriánként |
| `/label` | POST | Ismeretlen tárgy kézzel megcímkézése + újratanítás |

## ML modell

- **Algoritmus:** TF-IDF (char n-gram, 2-4) + Logistic Regression
- **Tanítóadat:** `data/training_data.csv` (szerkeszthető)
- **Kategóriák:** Élelmiszer, Vendéglátás, Közlekedés, Szórakozás, Sport, Rezsi, Online vásárlás, Egészség, Lakhatás, Utazás, Drogéria, Készpénz, Átutalás, Egyéb
- **Újratanítás:** `/label` végpont automatikusan újratanít, vagy manuálisan: `python train.py`

## Tesztek

```bash
pytest tests/ -v
```

GitHub Actions CI minden push-nál automatikusan futtatja a teszteket.

## Fájlstruktúra

```
├── sms_receiver.py            # Flask API
├── sms_parser.py              # SMS regex parser
├── categorizer.py             # ML modell
├── train.py                   # Tanítás / újratanítás
├── generate_training_data.py  # Seed tanítóadat generáló
├── tests/
│   ├── test_parser.py         # Parser tesztek
│   ├── test_categorizer.py    # ML modell tesztek
│   └── test_api.py            # API végpont tesztek
├── data/
│   └── training_data.csv      # ML tanítóadat
├── templates/
│   └── index.html             # Web dashboard
├── Dockerfile
└── docker-compose.yml
```
