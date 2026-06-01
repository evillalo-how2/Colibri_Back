from argparse import ArgumentParser

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.service import Currency, Service, ServiceModality, ServiceType
from app.schemas.service import ServiceCreate
from app.services.service_service import ServiceService


SEED_SERVICES = [
    {
        "name": "Sesión individual online",
        "short_description": "Acompañamiento psicológico individual por videollamada.",
        "description": (
            "Sesión enfocada en acompañamiento emocional, ansiedad, autoestima, "
            "vínculos y procesos personales. Ideal para adolescentes y adultos."
        ),
        "type": ServiceType.THERAPY,
        "modality": ServiceModality.ONLINE,
        "price_cents": 85000,
        "currency": Currency.MXN,
        "duration_minutes": 60,
        "is_stock_limited": False,
        "stock_quantity": None,
        "is_active": True,
        "is_public": True,
        "requires_appointment": True,
        "display_order": 1,
        "cover_image_url": None,
        "metadata": {
            "audience": "Adolescentes y adultos",
            "delivery_method": "Videollamada",
            "includes": ["Sesión de 60 minutos", "Orientación inicial"],
        },
    },
    {
        "name": "Sesión individual presencial",
        "short_description": "Sesión psicológica individual en consultorio.",
        "description": (
            "Espacio presencial de acompañamiento psicológico para trabajar "
            "procesos emocionales, toma de decisiones, ansiedad y autoestima."
        ),
        "type": ServiceType.THERAPY,
        "modality": ServiceModality.IN_PERSON,
        "price_cents": 95000,
        "currency": Currency.MXN,
        "duration_minutes": 60,
        "is_stock_limited": False,
        "stock_quantity": None,
        "is_active": True,
        "is_public": True,
        "requires_appointment": True,
        "display_order": 2,
        "cover_image_url": None,
        "metadata": {
            "audience": "Adolescentes y adultos",
            "location_notes": "Consultorio privado",
        },
    },
    {
        "name": "Taller de ansiedad",
        "short_description": "Taller práctico para entender y regular la ansiedad.",
        "description": (
            "Taller introductorio con ejercicios prácticos de respiración, "
            "identificación de pensamientos y herramientas de regulación emocional."
        ),
        "type": ServiceType.WORKSHOP,
        "modality": ServiceModality.HYBRID,
        "price_cents": 45000,
        "currency": Currency.MXN,
        "duration_minutes": 120,
        "is_stock_limited": False,
        "stock_quantity": None,
        "is_active": True,
        "is_public": True,
        "requires_appointment": True,
        "display_order": 3,
        "cover_image_url": None,
        "metadata": {
            "audience": "Personas con ansiedad leve o moderada",
            "includes": ["Material PDF", "Ejercicios guiados"],
        },
    },
    {
        "name": "Curso para padres",
        "short_description": "Curso de orientación emocional para madres y padres.",
        "description": (
            "Curso diseñado para madres, padres o cuidadores que buscan mejorar "
            "la comunicación emocional y acompañar mejor a niñas, niños o adolescentes."
        ),
        "type": ServiceType.COURSE,
        "modality": ServiceModality.ONLINE,
        "price_cents": 120000,
        "currency": Currency.MXN,
        "duration_minutes": 180,
        "is_stock_limited": False,
        "stock_quantity": None,
        "is_active": True,
        "is_public": False,
        "requires_appointment": False,
        "display_order": 4,
        "cover_image_url": None,
        "metadata": {
            "audience": "Madres, padres y cuidadores",
            "format": "Sesiones grabadas y material descargable",
        },
    },
    {
        "name": "Libro de ejercicios emocionales",
        "short_description": "Libro físico con ejercicios de autoconocimiento emocional.",
        "description": (
            "Libro práctico con ejercicios para identificar emociones, pensamientos, "
            "hábitos y herramientas de autocuidado."
        ),
        "type": ServiceType.BOOK,
        "modality": ServiceModality.NOT_APPLICABLE,
        "price_cents": 35000,
        "currency": Currency.MXN,
        "duration_minutes": None,
        "is_stock_limited": True,
        "stock_quantity": 15,
        "is_active": True,
        "is_public": True,
        "requires_appointment": False,
        "display_order": 5,
        "cover_image_url": None,
        "metadata": {
            "format": "Libro físico",
            "delivery_method": "Entrega local o envío",
        },
    },
    {
        "name": "Digital emotional workbook",
        "short_description": "Digital workbook for emotional self-awareness.",
        "description": (
            "A downloadable workbook with emotional awareness exercises, "
            "reflection prompts and self-care practices."
        ),
        "type": ServiceType.DIGITAL_PRODUCT,
        "modality": ServiceModality.DIGITAL,
        "price_cents": 1500,
        "currency": Currency.USD,
        "duration_minutes": None,
        "is_stock_limited": False,
        "stock_quantity": None,
        "is_active": True,
        "is_public": True,
        "requires_appointment": False,
        "display_order": 6,
        "cover_image_url": None,
        "metadata": {
            "format": "PDF",
            "language": "English",
            "delivery_method": "Download link",
        },
    },
    {
        "name": "Retiro de bienestar emocional",
        "short_description": "Experiencia grupal de bienestar y reflexión emocional.",
        "description": (
            "Retiro presencial con actividades guiadas de reflexión, regulación "
            "emocional, escritura terapéutica y dinámicas grupales."
        ),
        "type": ServiceType.RETREAT,
        "modality": ServiceModality.IN_PERSON,
        "price_cents": 250000,
        "currency": Currency.MXN,
        "duration_minutes": 480,
        "is_stock_limited": True,
        "stock_quantity": 12,
        "is_active": True,
        "is_public": False,
        "requires_appointment": True,
        "display_order": 7,
        "cover_image_url": None,
        "metadata": {
            "audience": "Adultos",
            "includes": ["Material de trabajo", "Coffee break"],
        },
    },
    {
        "name": "Producto digital de autocuidado",
        "short_description": "Material descargable para crear una rutina de autocuidado.",
        "description": (
            "Guía descargable con ejercicios simples para organizar una rutina "
            "personal de autocuidado emocional."
        ),
        "type": ServiceType.DIGITAL_PRODUCT,
        "modality": ServiceModality.DIGITAL,
        "price_cents": 19900,
        "currency": Currency.MXN,
        "duration_minutes": None,
        "is_stock_limited": False,
        "stock_quantity": None,
        "is_active": True,
        "is_public": True,
        "requires_appointment": False,
        "display_order": 8,
        "cover_image_url": None,
        "metadata": {
            "format": "PDF",
            "delivery_method": "Correo electrónico",
        },
    },
]


def _get_service_by_name(name: str) -> Service | None:
    db = SessionLocal()

    try:
        statement = select(Service).where(Service.name == name)
        return db.scalar(statement)

    finally:
        db.close()


def seed_services() -> None:
    db = SessionLocal()

    try:
        service_service = ServiceService(db)

        created_count = 0
        skipped_count = 0

        for service_data in SEED_SERVICES:
            existing_service = _get_service_by_name(service_data["name"])

            if existing_service:
                print(
                    f"Skipped existing service: "
                    f"{existing_service.catalog_code} | "
                    f"{existing_service.name}"
                )
                skipped_count += 1
                continue

            payload = ServiceCreate(**service_data)
            service = service_service.create_service(payload)

            print(
                f"Created service: {service.catalog_code} | "
                f"{service.name} ({service.currency})"
            )
            created_count += 1

        print("")
        print("Services seed completed.")
        print(f"Created: {created_count}")
        print(f"Skipped: {skipped_count}")

    finally:
        db.close()


def main() -> None:
    parser = ArgumentParser(description="Seed fake Psicomichi services.")
    parser.parse_args()

    seed_services()


if __name__ == "__main__":
    main()