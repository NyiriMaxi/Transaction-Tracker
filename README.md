# TransTracker — SMS fizetés követő

MacroDroid → Python API → ML kategorizáló → db

## Summary
 
Használathoz szükséges Macrodroid és Tailscale ha más hálózaton is szeretnénk. Macrodroidnál beállítandó hogy az SMS kitől jön, lehet ez telefonszám vagy névjegy, csak felismerje, majd a HTTP kéréseknél meg kell adni az API címet.
Amint ez megvan, minden tranzakció ami azon az értesítésen keresztül érkezik (és megadott formátumban van), megjelenik az adatbázisban, ahol szabadon kinyerhető akár havonta vagy az egész egyszerre kategóriánként besorolva.
ML segítségével történik a kategórizálás, így előfordulhat hogy rossz kategória lesz megadva, de kézzel is meg lehet adni a kategóriát /label POST kéréssel és további tanító anyagok közé rakni a train.py segítségével, amivel kiküszöbölhető a félrediagnosztikálás a következő alkalommal.

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
                    data/transactions.db
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
├── sms_parser.py         #SMS regex parser
├── categorizer.py        # ML modell
├── train.py              # Tanítás / újratanítás
├── generate_training_data.py  # Seed tanítóadat generáló
├── data/
│   ├── transactions.db  # Rögzített tranzakciók
│   └── training_data.csv # ML tanítóadat (szerkeszthető)
└── model/
    └── classifier.pkl    # Mentett modell
```
