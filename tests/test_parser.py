"""SMS parser tesztek."""

import pytest
from sms_parser import parse_sms, Transaction


VALID_SMS = (
    "Mastercard Standard POS tranzakció 5490Ft időpont: 2024.01.15 14:23:45 "
    "E: 45320 Ft Hely: LIDL HUNGARY KFT"
)


def test_parse_valid_sms():
    tx = parse_sms(VALID_SMS)
    assert tx is not None
    assert tx.amount == 5490.0
    assert tx.subject == "LIDL HUNGARY KFT"
    assert tx.date == "2024.01.15 14:23:45"


def test_parse_amount_with_spaces():
    sms = (
        "Mastercard Standard POS tranzakció 5 490Ft időpont: 2024.01.15 14:23:45 "
        "E: 45320 Ft Hely: LIDL HUNGARY KFT"
    )
    tx = parse_sms(sms)
    assert tx is not None
    assert tx.amount == 5490.0


def test_parse_amount_with_decimal():
    sms = (
        "Mastercard Standard POS tranzakció 1990,50Ft időpont: 2024.06.01 10:00:00 "
        "E: 10000 Ft Hely: BOLT"
    )
    tx = parse_sms(sms)
    assert tx is not None
    assert tx.amount == pytest.approx(1990.50)


def test_parse_accent_variant():
    """tranzakcio (ékezet nélkül) is működjön."""
    sms = (
        "Mastercard Standard POS tranzakcio 3000Ft időpont: 2024.03.10 09:00:00 "
        "E: 10000 Ft Hely: TESCO"
    )
    tx = parse_sms(sms)
    assert tx is not None
    assert tx.subject == "TESCO"


def test_parse_non_bank_sms_returns_none():
    assert parse_sms("bingchilling") is None


def test_parse_missing_subject_returns_none():
    sms = "Mastercard Standard POS tranzakció 1000Ft időpont: 2024.01.01 12:00:00"
    assert parse_sms(sms) is None


def test_parse_raw_sms_stored():
    tx = parse_sms(VALID_SMS)
    assert tx.raw_sms == VALID_SMS
