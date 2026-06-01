from argparse import ArgumentParser
from getpass import getpass

from app.core.exceptions import BadRequestError
from app.core.password_policy import validate_password_strength
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User, UserType
from app.repositories.user_repository import UserRepository


SEED_USERS = [
    {
        "email": "admin@psicomichi.com",
        "full_name": "Admin Psicomichi",
        "user_type": UserType.ADMIN,
        "is_superuser": True,
    },
    {
        "email": "psicologa@psicomichi.com",
        "full_name": "Psicóloga Psicomichi",
        "user_type": UserType.PSYCHOLOGIST,
        "is_superuser": False,
    },
    {
        "email": "asistente@psicomichi.com",
        "full_name": "Asistente Psicomichi",
        "user_type": UserType.ASSISTANT,
        "is_superuser": False,
    },
    {
        "email": "cliente@psicomichi.com",
        "full_name": "Cliente Psicomichi",
        "user_type": UserType.CLIENT,
        "is_superuser": False,
    },
]


def _get_seed_password(argument_password: str | None) -> str:
    if argument_password:
        return argument_password

    password = getpass("Seed users password: ").strip()
    password_confirmation = getpass("Confirm seed users password: ").strip()

    while not password or password != password_confirmation:
        print("")
        print("❌ Passwords do not match or are empty.")
        print("")

        password = getpass("Seed users password: ").strip()
        password_confirmation = getpass("Confirm seed users password: ").strip()

    return password


def _print_password_policy_error(error: BadRequestError) -> None:
    print("")
    print("❌ Invalid password for seed users.")
    print("")

    errors = str(error).split(". ")

    for item in errors:
        clean_item = item.strip().rstrip(".")

        if clean_item:
            print(f" - {clean_item}.")

    print("")
    print("Please try again with a stronger password.")
    print("")


def seed_users(password: str) -> None:
    validate_password_strength(password)

    db = SessionLocal()

    try:
        user_repository = UserRepository(db)
        password_hash = hash_password(password)

        created_count = 0
        skipped_count = 0

        for seed_user in SEED_USERS:
            existing_user = user_repository.get_by_email(seed_user["email"])

            if existing_user:
                print(f"Skipped existing user: {seed_user['email']}")
                skipped_count += 1
                continue

            user = User(
                email=seed_user["email"],
                full_name=seed_user["full_name"],
                password_hash=password_hash,
                user_type=seed_user["user_type"],
                is_active=True,
                is_superuser=seed_user["is_superuser"],
            )

            user_repository.create(user)

            print(f"Created user: {seed_user['email']}")
            created_count += 1

        print("")
        print("✅ Seed completed.")
        print(f"Created: {created_count}")
        print(f"Skipped: {skipped_count}")

    finally:
        db.close()


def main() -> None:
    parser = ArgumentParser(description="Seed initial Psicomichi users.")
    parser.add_argument(
        "--password",
        type=str,
        default=None,
        help="Password for all seed users. Use only in local development.",
    )

    args = parser.parse_args()
    password = _get_seed_password(args.password)

    try:
        seed_users(password)
    except BadRequestError as error:
        _print_password_policy_error(error)


if __name__ == "__main__":
    main()