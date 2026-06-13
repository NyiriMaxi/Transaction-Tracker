"""
Szintetikus tanítóadat generáló.
Futtatás: python generate_training_data.py
Hozzáfűzi az új adatokat a training_data.csv-hez.
"""

import csv
import os
import random

TRAINING_DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "training_data.csv")

# (tárgy variáns, kategória) lista
EXAMPLES = {
    "Élelmiszer": [
        "LIDL", "LIDL HUNGARY", "LIDL HUNGARY KFT", "LIDL 1234",
        "SPAR", "SPAR MAGYARORSZÁG", "SPAR MAGYARORSZAG", "SPAR SZUPERMARKET",
        "TESCO", "TESCO ÁRUHÁZ", "TESCO EXTRA", "TESCO EXPRESS",
        "ALDI", "ALDI MAGYARORSZÁG", "ALDI STORE",
        "PENNY", "PENNY MARKET", "PENNY MARKET KFT",
        "CBA", "CBA KÖZÉRT", "CBA SZUPERMARKET",
        "AUCHAN", "AUCHAN BUDAÖRS", "AUCHAN HYPERMARKET",
        "INTERSPAR", "INTERSPAR HYPERMARKET",
        "PÉKSÉG", "PÉKÁRU", "PÉK",
        "HENTES", "HÚSBOLT",
        "ZÖLDSÉGES", "ZÖLDSÉG GYÜMÖLCS",
        "ÉLELMISZER", "KÖZÉRT",
        "SUPERMARKET", "GROCERY",
    ],
    "Drogéria": [
        "DM", "DM DROGERIE", "DM DROGERIEMARKT",
        "ROSSMANN", "ROSSMANN DROGUÉRIA",
        "MÜLLER", "MULLER",
        "DOUGLAS", "DOUGLAS PARFÜMÉRIA",
        "NOTINO", "PARFÜM",
        "KOZMETIKA", "DROGUÉRIA", "DROGERIA",
    ],
    "Közlekedés": [
        "MOL", "MOL TÖLTŐÁLLOMÁS", "MOL BENZINKÚT", "MOL 1234",
        "OMV", "OMV BENZINKÚT",
        "SHELL", "SHELL BENZINKÚT",
        "BKK", "BKV", "METRO JEGY", "BUSZ JEGY",
        "VOLÁNBUSZ", "VOLÁN",
        "MÁV", "MAV", "MAVINFORM", "VONAT JEGY",
        "PARKING", "PARKOLÓ", "PARKOLÁS",
        "AUTÓPÁLYA", "ÚTDÍJ", "HU-GO",
    ],
    "Utazás": [
        "RYANAIR", "RYAN AIR",
        "SZALLAS.HU", "SZALLAS HU",
        "SZÁLLODA", "HOTEL", "HOSTEL", "PANZIÓ",
    ],
    "Szórakozás": [
        "NETFLIX", "NETFLIX.COM",
        "SPOTIFY", "SPOTIFY AB",
        "YOUTUBE", "YOUTUBE PREMIUM",
        "STEAM", "STEAM GAMES",
        "MOZI", "CINEMA CITY",
    ],
    "Vendéglátás": [
        "MCDONALD'S", "MCDONALDS", "MEKK",
        "KFC", "BURGER KING", "BURGERKINGS",
        "PIZZA HUT", "DOMINO'S", "DOMINÓS", "PIZZÉRIA",
        "STARBUCKS", "STARBUCKS COFFEE",
        "WOLT", "FOODPANDA", "NETPINCÉR",
        "ÉTTEREM", "RESTAURANT", "BISTRO", "BISZTRÓ",
        "FALATOZÓ", "GYROS", "KEBAB",
        "SÖRÖZŐ", "PUB", "BAR", "KOCSMA",
        "KÁVÉZÓ", "CAFÉ", "COFFEE",
        "PIZZA", "SUSHI", "THAI",
        "EBÉD", "VACSORA",
    ],
    "Online vásárlás": [
        "AMAZON", "AMAZON.DE", "AMAZON EU",
        "EMAG", "EMAG.HU",
        "ALIEXPRESS", "ALI EXPRESS",
        "EBAY",
        "ALZA", "ALZA.HU",
        "MEDIAMARKT", "MEDIA MARKT",
        "EURONICS",
        "APPLE STORE", "GOOGLE PLAY",
    ],
    "Sport": [
        "GYM", "EDZŐTEREM",
    ],
    "Készpénz": [
        "ATM", "ATM FELVÉTEL",
        "készpénzfelvétel", "KÉSZPÉNZFELVÉTEL",
        "bankautomata", "BANKAUTOMATA",
        "CASH", "KESZPENZ",
    ],
    "Átutalás": [
        "átutalás", "ÁTUTALÁS",
        "utalás", "UTALÁS",
        "banki átutalás",
        "berlet", "BÉRLET",
        "számla", "SZÁMLA",
        "díj", "DÍJ",
    ],
    "Egyéb": [
        "ismeretlen", "ISMERETLEN",
        "egyéb", "EGYÉB",
        "VEGYES",
        "MISCELLANEOUS",
    ],
}


def main():
    rows = []
    for category, subjects in EXAMPLES.items():
        for subject in subjects:
            rows.append({"subject": subject, "category": category})

    # Shuffle
    random.seed(42)
    random.shuffle(rows)

    with open(TRAINING_DATA_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["subject", "category"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(rows)} sor írva → {TRAINING_DATA_PATH}")
    category_counts = {}
    for r in rows:
        category_counts[r["category"]] = category_counts.get(r["category"], 0) + 1
    for cat, cnt in sorted(category_counts.items()):
        print(f"  {cat:<25} {cnt:>3} példa")


if __name__ == "__main__":
    main()
