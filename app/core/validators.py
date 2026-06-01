import re
from datetime import date

from app.core.exceptions import BadRequestError
from app.models.patient import PatientGender


GENDER_LABEL_MAP = {
    "male": PatientGender.MALE.value,
    "hombre": PatientGender.MALE.value,
    "female": PatientGender.FEMALE.value,
    "mujer": PatientGender.FEMALE.value,
    "non_binary": PatientGender.NON_BINARY.value,
    "no binario": PatientGender.NON_BINARY.value,
    "no_binario": PatientGender.NON_BINARY.value,
}

NAME_PATTERN = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s'.-]+$")

REALISTIC_EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]{2,}@[A-Za-z0-9-]{2,}(\.[A-Za-z]{2,})+$"
)

MIN_BIRTH_DATE = date(1900, 1, 1)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_full_name(full_name: str) -> None:
    normalized_name = full_name.strip()

    if len(normalized_name) < 2:
        raise BadRequestError("Full name must be at least 2 characters long.")

    if len(normalized_name) > 255:
        raise BadRequestError("Full name must be at most 255 characters long.")

    if not NAME_PATTERN.fullmatch(normalized_name):
        raise BadRequestError(
            "Full name contains invalid characters."
        )

    if "  " in normalized_name:
        raise BadRequestError("Full name must not contain repeated spaces.")

def normalize_mexican_phone(phone: str | None) -> str | None:
    if phone is None:
        return None

    normalized_phone = phone.strip()

    if not normalized_phone:
        return None

    if not normalized_phone.isdigit() or len(normalized_phone) != 10:
        raise BadRequestError("Phone must contain exactly 10 digits.")

    return normalized_phone

def validate_realistic_email(email: str | None) -> str | None:
    if email is None:
        return None

    normalized_email = normalize_email(email)

    if not normalized_email:
        return None

    if not REALISTIC_EMAIL_PATTERN.fullmatch(normalized_email):
        raise BadRequestError("Email must be a valid email address.")

    domain = normalized_email.split("@", 1)[1]
    labels = domain.split(".")

    for label in labels:
        if label.startswith("-") or label.endswith("-"):
            raise BadRequestError("Email must be a valid email address.")

    return normalized_email


def validate_birth_date(birth_date: date | None) -> date | None:
    if birth_date is None:
        return None

    today = date.today()

    if birth_date > today:
        raise BadRequestError("Birth date cannot be in the future.")

    if birth_date < MIN_BIRTH_DATE:
        raise BadRequestError("Birth date is too old.")

    return birth_date

def normalize_patient_gender(gender: str | PatientGender | None) -> str | None:
    if gender is None:
        return None

    if isinstance(gender, PatientGender):
        return gender.value

    normalized_gender = gender.strip().lower()

    if not normalized_gender:
        return None

    mapped_gender = GENDER_LABEL_MAP.get(normalized_gender)

    if not mapped_gender:
        raise BadRequestError("Gender must be male, female or non_binary.")

    return mapped_gender