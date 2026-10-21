import re

from app.database import insert_lead


def create_lead(payload):
    """Form bilgilerini kontrol eder ve veritabanına kaydeder."""
    if not isinstance(payload, dict):
        raise ValueError("Form verisi bir JSON nesnesi olmalı.")

    fields = {
        "full_name": (150, True),
        "company": (200, False),
        "email": (254, True),
        "phone": (30, False),
        "message": (5000, True),
    }

    data = {}

    for field, (max_length, required) in fields.items():
        value = payload.get(field, "")

        if not isinstance(value, str):
            raise ValueError(f"{field} alanı metin olmalı.")

        value = value.strip()

        if required and not value:
            raise ValueError(f"{field} alanı zorunlu.")

        if len(value) > max_length:
            raise ValueError(
                f"{field} en fazla {max_length} karakter olabilir."
            )

        data[field] = value

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", data["email"]):
        raise ValueError("Geçerli bir e-posta adresi gir.")

    return insert_lead(data)