import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.employee_profile import EmploymentType


class EmployeeProfileBase(BaseModel):
    legal_name: str | None = Field(default=None, max_length=255)
    preferred_name: str | None = Field(default=None, max_length=255)
    birth_date: date | None = None
    gender: str | None = Field(default=None, max_length=50)

    phone: str | None = Field(default=None, max_length=30)
    emergency_contact_name: str | None = Field(default=None, max_length=255)
    emergency_contact_phone: str | None = Field(default=None, max_length=30)

    address_line: str | None = Field(default=None, max_length=255)
    neighborhood: str | None = Field(default=None, max_length=150)
    city: str | None = Field(default=None, max_length=150)
    state: str | None = Field(default=None, max_length=150)
    zip_code: str | None = Field(default=None, max_length=20)
    country: str | None = Field(default="México", max_length=100)

    job_title: str | None = Field(default=None, max_length=150)
    department: str | None = Field(default=None, max_length=150)
    employment_type: EmploymentType | None = None
    hire_date: date | None = None
    termination_date: date | None = None
    work_schedule: str | None = Field(default=None, max_length=255)
    notes: str | None = None

    curp: str | None = Field(default=None, max_length=18)
    rfc: str | None = Field(default=None, max_length=13)
    nss: str | None = Field(default=None, max_length=15)
    professional_license: str | None = Field(default=None, max_length=50)

    ine_document_note: str | None = Field(default=None, max_length=255)
    curp_document_note: str | None = Field(default=None, max_length=255)
    rfc_document_note: str | None = Field(default=None, max_length=255)
    nss_document_note: str | None = Field(default=None, max_length=255)
    proof_of_address_note: str | None = Field(default=None, max_length=255)
    professional_license_note: str | None = Field(default=None, max_length=255)
    contract_document_note: str | None = Field(default=None, max_length=255)
    documents_notes: str | None = None


class EmployeeProfileCreate(EmployeeProfileBase):
    pass


class EmployeeProfileUpdate(EmployeeProfileBase):
    pass


class EmployeeProfileUpsert(EmployeeProfileBase):
    pass


class EmployeeProfileResponse(EmployeeProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)