from argparse import ArgumentParser
from datetime import date
from random import Random

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.patient import Patient, PatientModality, PatientStatus
from app.schemas.patient import PatientCreate
from app.services.patient_service import PatientService


FIRST_NAMES = [
    "Monserrat",
    "Valeria",
    "Sofía",
    "Camila",
    "Mariana",
    "Fernanda",
    "Regina",
    "Daniela",
    "Paola",
    "Andrea",
    "Luis",
    "Carlos",
    "Miguel",
    "Diego",
    "Jorge",
    "Emiliano",
    "Fernando",
    "Alejandro",
    "Ricardo",
    "Mateo",
]

LAST_NAMES = [
    "Pérez",
    "Gómez",
    "Hernández",
    "Martínez",
    "López",
    "Sánchez",
    "Ramírez",
    "Torres",
    "Flores",
    "Rivera",
    "Castillo",
    "Morales",
    "Vargas",
    "Cruz",
    "Ortega",
]

SOURCES = [
    "instagram",
    "whatsapp",
    "referido",
    "landing",
    "facebook",
    "otro",
]

INITIAL_REASONS = [
    "Quiere iniciar proceso terapéutico.",
    "Busca apoyo por ansiedad.",
    "Solicita orientación emocional.",
    "Tiene interés en terapia individual.",
    "Desea mejorar manejo de estrés.",
    "Busca seguimiento psicológico.",
    "Pregunta por disponibilidad de horarios.",
    "Solicita información de modalidad online.",
    "Fue referido por otro paciente.",
    "Quiere retomar terapia después de una pausa.",
]

INTERNAL_NOTES = [
    "Contactar por WhatsApp después de las 6pm.",
    "Prefiere comunicación por mensaje.",
    "Pidió información de costos antes de agendar.",
    "Pendiente confirmar disponibilidad.",
    "Interesado en sesiones semanales.",
    "Prefiere modalidad online.",
    "Preguntar por horario matutino.",
    "Requiere seguimiento administrativo.",
    "Sin notas adicionales por ahora.",
]


def _build_fake_patient(index: int, rng: Random) -> PatientCreate:
    first_name = rng.choice(FIRST_NAMES)
    last_name = rng.choice(LAST_NAMES)
    second_last_name = rng.choice(LAST_NAMES)

    full_name = f"{first_name} {last_name} {second_last_name}"

    birth_date = date(
        rng.randint(1980, 2006),
        rng.randint(1, 12),
        rng.randint(1, 28),
    )

    return PatientCreate(
        full_name=full_name,
        email=f"paciente.fake.{index:03d}@example.com",
        phone=f"55{rng.randint(10000000, 99999999)}",
        birth_date=birth_date,
        gender=rng.choice(["female", "male", "non_binary"]),
        preferred_modality=rng.choice(list(PatientModality)),
        status=rng.choice(list(PatientStatus)),
        source=rng.choice(SOURCES),
        initial_reason=rng.choice(INITIAL_REASONS),
        internal_notes=rng.choice(INTERNAL_NOTES),
        is_active=True,
    )


def _patient_exists_by_email(email: str) -> bool:
    db = SessionLocal()

    try:
        statement = select(Patient).where(Patient.email == email)
        patient = db.scalar(statement)

        return patient is not None

    finally:
        db.close()


def seed_patients(count: int) -> None:
    rng = Random(2026)
    db = SessionLocal()

    try:
        patient_service = PatientService(db)

        created_count = 0
        skipped_count = 0

        for index in range(1, count + 1):
            payload = _build_fake_patient(index, rng)

            if _patient_exists_by_email(str(payload.email)):
                print(f"Skipped existing patient: {payload.email}")
                skipped_count += 1
                continue

            patient = patient_service.create_patient(payload)

            print(f"Created patient: {patient.full_name} <{patient.email}>")
            created_count += 1

        print("")
        print("Patients seed completed.")
        print(f"Created: {created_count}")
        print(f"Skipped: {skipped_count}")

    finally:
        db.close()


def main() -> None:
    parser = ArgumentParser(description="Seed fake Psicomichi patients.")
    parser.add_argument(
        "--count",
        type=int,
        default=20,
        help="Number of fake patients to create.",
    )

    args = parser.parse_args()

    if args.count < 1:
        raise ValueError("Count must be greater than zero.")

    seed_patients(args.count)


if __name__ == "__main__":
    main()