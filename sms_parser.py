"""
MBH Bank SMS parser.

Pontos formátum:
  "Mastercard Standard POS tranzakció 5490Ft időpont: 2024.01.15 14:23:45 E: 45320 Ft Hely: LIDL HUNGARY KFT"
"""

import re
from dataclasses import dataclass
from typing import Optional

# Összeg: közvetlenül a "tranzakció" után, pl. "5490Ft" vagy "5 490Ft" vagy "5 490,50Ft"
_AMOUNT_RE = re.compile(r"tranzakci[oóò]\s+([\d\s]+(?:,\d{1,2})?)\s*Ft", re.IGNORECASE)

# Dátum: "időpont: 2024.01.15 14:23:45"
_DATE_RE = re.compile(r"id[oő]pont:\s*(\d{4}\.\d{2}\.\d{2}\s+\d{2}:\d{2}:\d{2})", re.IGNORECASE)

# Hely (tárgy): "Hely: <minden a sor végéig>"
_SUBJECT_RE = re.compile(r"[Hh]ely:\s*(.+)$", re.IGNORECASE)


@dataclass
class Transaction:
    amount: float
    subject: str
    date: str        # az SMS-ben lévő dátum, pl. "2024.01.15 14:23:45"
    raw_sms: str


def parse_sms(sms: str) -> Optional[Transaction]:
    amount_match = _AMOUNT_RE.search(sms)
    subject_match = _SUBJECT_RE.search(sms.strip())

    if not amount_match or not subject_match:
        return None

    raw_amount = amount_match.group(1).replace(" ", "").replace(",", ".")
    try:
        amount = float(raw_amount)
    except ValueError:
        return None

    subject = subject_match.group(1).strip()

    date_match = _DATE_RE.search(sms)
    date = date_match.group(1).strip() if date_match else ""

    return Transaction(
        amount=amount,
        subject=subject,
        date=date,
        raw_sms=sms,
    )
