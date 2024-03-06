from datetime import datetime
from typing import TypeVar, Generic, Optional

from pydantic import Field, BaseModel

T = TypeVar('T')


class CommonFileResponse:
    def __init__(self, file_path, file_name):
        self.file_path = file_path
        self.file_name = file_name


class GenericResponse(BaseModel, Generic[T]):
    response_date: Optional[datetime] = Field(..., alias="response_date")
    status_code: str
    body: T

    @classmethod
    def generate_generic_response(cls, body: T, status_code: str) -> "GenericResponse[T]":
        return cls(response_date=datetime.now(), status_code=status_code, body=body)

    @classmethod
    def generate_success_response(cls, body: T) -> "GenericResponse[T]":
        return cls(response_date=datetime.now(), status_code="SUCCESS", body=body)
