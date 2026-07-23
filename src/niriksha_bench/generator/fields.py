import random
import string
from datetime import date, timedelta

from .schemas import DocumentFields

FIRST = ["AARAV", "ADITI", "ANANYA", "ARJUN", "DEV", "DIYA", "ISHAN", "KAVYA", "MEERA", "NEEL", "PRIYA", "RAHUL", "RIYA", "ROHAN", "SANA", "VIKRAM"]
LAST = ["BANERJEE", "DESAI", "GUPTA", "IYER", "JOSHI", "KAPOOR", "KHAN", "KULKARNI", "MEHTA", "NAIR", "PATEL", "RAO", "SEN", "SHAH", "SHARMA", "SINGH"]


def identity_number(rng: random.Random) -> str:
    return (
        "".join(rng.choices(string.ascii_uppercase, k=3))
        + "".join(rng.choices(string.digits, k=6))
        + rng.choice(string.ascii_uppercase)
    )


def generate_fields(index: int, rng: random.Random) -> DocumentFields:
    name = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
    guardian = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
    start = date(1960, 1, 1)
    dob = start + timedelta(days=rng.randrange((date(2005, 1, 1) - start).days))
    return DocumentFields(
        full_name=name,
        guardian_name=guardian,
        date_of_birth=dob.isoformat(),
        identity_number=identity_number(rng),
        document_id=f"SYN-{index:06d}",
    )
