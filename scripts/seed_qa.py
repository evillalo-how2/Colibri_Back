from scripts.seed_patients import seed_patients
from scripts.seed_services import seed_services
from scripts.seed_users import seed_users


def main() -> None:
    default_password = "NubeMorada123!"

    print("Seeding QA users...")
    seed_users(default_password)

    print("Seeding QA patients...")
    seed_patients(25)

    print("Seeding QA services...")
    seed_services()

    print("QA seed completed.")


if __name__ == "__main__":
    main()