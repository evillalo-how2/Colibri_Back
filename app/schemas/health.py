from pydantic import BaseModel


class HealthCheckResponse(BaseModel):
    status: str
    app_name: str
    environment: str
    database: str