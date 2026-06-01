import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_catalog_manager_user,
    get_current_staff_user,
)
from app.db.session import get_db
from app.models.service import ServiceModality, ServiceType
from app.models.user import User
from app.schemas.service import (
    ServiceCreate,
    ServiceResponse,
    ServicesListResponse,
    ServiceUpdate,
)
from app.services.service_service import ServiceService

router = APIRouter()


@router.post(
    "",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service(
    payload: ServiceCreate,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[
        User,
        Depends(get_current_catalog_manager_user),
    ],
) -> ServiceResponse:
    service_service = ServiceService(db)
    service = service_service.create_service(payload)

    return ServiceResponse.model_validate(service)


@router.get(
    "",
    response_model=ServicesListResponse,
)
def list_services(
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_staff_user)],
    search: Annotated[
        str | None,
        Query(min_length=1, max_length=255),
    ] = None,
    service_type: Annotated[
        ServiceType | None,
        Query(alias="type"),
    ] = None,
    modality: ServiceModality | None = None,
    is_active: bool | None = None,
    is_public: bool | None = None,
    requires_appointment: bool | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ServicesListResponse:
    service_service = ServiceService(db)
    services, total = service_service.list_services(
        search=search,
        service_type=service_type,
        modality=modality,
        is_active=is_active,
        is_public=is_public,
        requires_appointment=requires_appointment,
        page=page,
        limit=limit,
    )

    return ServicesListResponse(
        items=[
            ServiceResponse.model_validate(service)
            for service in services
        ],
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/{service_id}",
    response_model=ServiceResponse,
)
def get_service(
    service_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[User, Depends(get_current_staff_user)],
) -> ServiceResponse:
    service_service = ServiceService(db)
    service = service_service.get_service_by_id(service_id)

    return ServiceResponse.model_validate(service)


@router.patch(
    "/{service_id}",
    response_model=ServiceResponse,
)
def update_service(
    service_id: uuid.UUID,
    payload: ServiceUpdate,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[
        User,
        Depends(get_current_catalog_manager_user),
    ],
) -> ServiceResponse:
    service_service = ServiceService(db)
    service = service_service.update_service(
        service_id=service_id,
        payload=payload,
    )

    return ServiceResponse.model_validate(service)


@router.patch(
    "/{service_id}/activate",
    response_model=ServiceResponse,
)
def activate_service(
    service_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[
        User,
        Depends(get_current_catalog_manager_user),
    ],
) -> ServiceResponse:
    service_service = ServiceService(db)
    service = service_service.activate_service(service_id)

    return ServiceResponse.model_validate(service)


@router.patch(
    "/{service_id}/deactivate",
    response_model=ServiceResponse,
)
def deactivate_service(
    service_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[
        User,
        Depends(get_current_catalog_manager_user),
    ],
) -> ServiceResponse:
    service_service = ServiceService(db)
    service = service_service.deactivate_service(service_id)

    return ServiceResponse.model_validate(service)


@router.patch(
    "/{service_id}/publish",
    response_model=ServiceResponse,
)
def publish_service(
    service_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[
        User,
        Depends(get_current_catalog_manager_user),
    ],
) -> ServiceResponse:
    service_service = ServiceService(db)
    service = service_service.publish_service(service_id)

    return ServiceResponse.model_validate(service)


@router.patch(
    "/{service_id}/unpublish",
    response_model=ServiceResponse,
)
def unpublish_service(
    service_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    _current_user: Annotated[
        User,
        Depends(get_current_catalog_manager_user),
    ],
) -> ServiceResponse:
    service_service = ServiceService(db)
    service = service_service.unpublish_service(service_id)

    return ServiceResponse.model_validate(service)