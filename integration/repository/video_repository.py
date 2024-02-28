from sqlalchemy.orm import Session
from models.entities import VideoFileStoragesEntity


def get_video_by_filename(db: Session, filename: str) -> VideoFileStoragesEntity | None:
    video_file_storage = db.query(VideoFileStoragesEntity).filter(VideoFileStoragesEntity.file_name == filename).first()
    if video_file_storage:
        return video_file_storage
    return None


def create(db: Session, video_file_storage: VideoFileStoragesEntity) -> VideoFileStoragesEntity:
    db.add(video_file_storage)
    db.commit()
    db.refresh(video_file_storage)
    return video_file_storage