from typing import List, Optional

from pydantic import BaseModel, Field

from models.entities import VideoFileStoragesEntity


class MinIORequest(BaseModel):
    event_name: str = Field(..., alias="EventName")
    key: str = Field(..., alias="Key")
    records: List[dict] = Field(..., alias="Records")

    class Config:
        populate_by_name = True

    @staticmethod
    def convert_to_video_file_storage_entity(minio_request):
        video_file_storage_entity = VideoFileStoragesEntity()
        video_file_storage_entity.size = str(minio_request.records[0].get("s3").get("object").get("size"))
        return video_file_storage_entity


class ConvertSrtRequest:
    def __init__(self, code: str,  voice_name: Optional[str] = "None", gender: Optional[str] = "None"):
        self.voice_name = voice_name
        self.gender = gender
        self.code = code
