from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from config.database import get_db

router = APIRouter(
    prefix="/videos",
    tags=["videos"]
)


@router.get("/filter")
async def get_all():
    return {"data": "All videos"}


@router.post("/files")
async def create():
    return {"data": "File created"}


@router.post("/youtube-links")
async def upload_by_youtube(db: Session = Depends(get_db)):
    return {"data": "Youtube link uploaded"}
