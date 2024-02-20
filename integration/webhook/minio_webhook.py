from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.database import get_db
from models.requests import MinIORequest
from services import video_service

router = APIRouter(
    prefix="/events",
    tags=["events"]
)


@router.post("/upload-file")
async def upload_file(body: MinIORequest, db: Session = Depends(get_db)):
    video_service.handle_minio_notification(db, body)
    return body
