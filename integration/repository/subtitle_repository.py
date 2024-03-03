from sqlalchemy.orm import Session
from models.entities import SubtitleFileStorageEntity


def create(db: Session, subtitle_file_storage: SubtitleFileStorageEntity) -> SubtitleFileStorageEntity:
    db.add(subtitle_file_storage)
    db.commit()
    db.refresh(subtitle_file_storage)
    return subtitle_file_storage
