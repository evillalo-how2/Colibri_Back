import re

from app.core.exceptions import BadRequestError

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128

COMMON_PASSWORD_KEYWORDS = {
    "password",
    "admin",
    "qwerty",
    "123456",
    "12345678",
    "123456789",
    "psicomichi",
    "letmein",
    "welcome",
    "iloveyou",
}


def validate_password_strength(
    password: str,
    *,
    email: str | None = None,
    full_name: str | None = None,
) -> None:
    errors: list[str] = []

    if len(password) < MIN_PASSWORD_LENGTH:
        errors.append(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters long."
        )

    if len(password) > MAX_PASSWORD_LENGTH:
        errors.append(
            f"Password must be at most {MAX_PASSWORD_LENGTH} characters long."
        )

    if any(character.isspace() for character in password):
        errors.append("Password must not contain spaces.")

    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")

    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")

    if not re.search(r"\d", password):
        errors.append("Password must contain at least one number.")

    if not re.search(r"[^a-zA-Z0-9]", password):
        errors.append("Password must contain at least one special character.")

    normalized_password = password.lower()

    for keyword in COMMON_PASSWORD_KEYWORDS:
        if keyword in normalized_password:
            errors.append("Password must not contain common words or patterns.")
            break

    if email:
        email_name = email.split("@")[0].lower()

        if email_name and email_name in normalized_password:
            errors.append("Password must not contain your email username.")

    if full_name:
        name_parts = [
            part.lower()
            for part in full_name.split()
            if len(part.strip()) >= 3
        ]

        for part in name_parts:
            if part in normalized_password:
                errors.append("Password must not contain your name.")

    if errors:
        raise BadRequestError(" ".join(errors))