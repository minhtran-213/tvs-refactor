from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.database import get_db
from services import locale_service

router = APIRouter(
    prefix="/locales",
    tags=["locales"]
)


@router.get("")
async def get_all(db: Session = Depends(get_db)):
    return locale_service.get_all(db)
