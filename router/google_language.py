from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from config.database import get_db
from services import google_languages_service

router = APIRouter(
    prefix="/google_languages",
    tags=["google_languages"]
)


@router.put("", status_code=status.HTTP_204_NO_CONTENT)
def update(db: Session = Depends(get_db)):
    return google_languages_service.update_locale_id(db)
