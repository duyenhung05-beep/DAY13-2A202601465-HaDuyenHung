from app.pii import scrub_text, scrub_value


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "REDACTED_PHONE_VN" in out


def test_scrub_value_redacts_nested_structures() -> None:
    out = scrub_value({"payload": [{"email": "student@vinuni.edu.vn"}, "090 123 4567"]})
    assert out == {
        "payload": [{"email": "[REDACTED_EMAIL]"}, "[REDACTED_PHONE_VN]"]
    }
