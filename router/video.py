from fastapi import APIRouter, Depends, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from models.enums import VideoOptionRequest
from config.database import get_db
from models.requests import YoutubeLinkUploadRequest
from models.responses import GenericResponse
from services import video_service

router = APIRouter(
    prefix="/videos",
    tags=["videos"]
)


@router.get("/filter")
async def get_all(
        db: Session = Depends(get_db)
):
    pass


@router.post("/files", status_code=200)
async def create(background_task: BackgroundTasks,
                 db: Session = Depends(get_db),
                 files: List[UploadFile] = File(...),
                 user_id: str = Form(...),
                 video_option_request: List[VideoOptionRequest] = Form(...),
                 output_language: str = Form(...)
                 ):
    video_service.process_uploaded_files(background_task, db, files, user_id, video_option_request, output_language)
    return GenericResponse.generate_generic_response(body="SUCCESS", status_code="2000")


@router.post("/youtube-links")
async def upload_by_youtube(background_task: BackgroundTasks,
                            youtube_request: YoutubeLinkUploadRequest,
                            db: Session = Depends(get_db)):
    video_service.process_youtube_links(background_task, db, youtube_request)
