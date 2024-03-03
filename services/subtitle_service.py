from sqlalchemy.orm import Session

from models.entities import SubtitleFileStorageEntity
from integration.repository import subtitle_repository


def save_uploaded_subtitles(db: Session, video_id: int):
    en_sub = SubtitleFileStorageEntity()
    en_sub.file_path = "en_sub"
    en_sub.file_name = "en_sub"
    en_sub.video_file_id = video_id
    en_sub.type = "ORIGIN"
    subtitle_repository.create(db, en_sub)
    translated_sub = SubtitleFileStorageEntity()
    translated_sub.file_path = "translated_sub"
    translated_sub.file_name = "translated_sub"
    translated_sub.video_file_id = video_id
    translated_sub.type = "TRANSLATED"
    subtitle_repository.create(db, translated_sub)
