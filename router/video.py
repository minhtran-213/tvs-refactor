from fastapi import APIRouter, Depends, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from models.enums import VideoOptionRequest
from config.database import get_db

router = APIRouter(
    prefix="/videos",
    tags=["videos"]
)


@router.get("/filter")
async def get_all():
    return {"data": "All videos"}


@router.post("/files")
async def create(db: Session = Depends(get_db),
                 files: List[UploadFile] = File(...),
                 user_id: str = Form(...),
                 video_option_request: VideoOptionRequest = Form(...),
                 output_language: str = Form(...),
                 labels: Optional[str] = Form(None)
                 ):
    return {"data": "File created"}


@router.post("/youtube-links")
async def upload_by_youtube(db: Session = Depends(get_db)):
    return {"data": "Youtube link uploaded"}
