from sqlalchemy.orm import Session

from config import utils
from models.entities import VideoFileStoragesEntity
from models.requests import MinIORequest
from models.enums import ProcessStatus
from integration.third_party import minio_client, ffmpeg, fastapi
from services import locale_service


def handle_minio_notification(db: Session, minio_request: MinIORequest):
    video_file_storage: VideoFileStoragesEntity = MinIORequest.convert_to_video_file_storage_entity(minio_request)
    video_information = __get_video_file_information_from_filepath(minio_request.key)
    video_file_storage = __convert_video_information_to_entity(video_information, video_file_storage)

    locale_code = video_information['basename'].split("_")[1]
    locale = locale_service.get_by_code(db, locale_code)
    video_file_storage.output_locale_id = locale.id

    db.add(video_file_storage)
    db.commit()
    return {"data": "File created"}


def __convert_video_information_to_entity(video_information: dict, video_file_storage: VideoFileStoragesEntity):
    video_file_storage.external_file_path = video_information['file_path']
    video_file_storage.content_type = video_information['content-type']
    video_file_storage.file_duration = video_information['duration']
    video_file_storage.file_resolution = video_information['resolution']
    video_file_storage.file_name = video_information['filename']
    video_file_storage.process_status = ProcessStatus.PROCESSING
    video_file_storage.file_extension = video_information['extension']
    return video_file_storage


def processing_video(file_path: str, locale_code: str):
    transcribe_result = fastapi.process_srt(file_path)
    origin_path = utils.get_dirname(transcribe_result['srt_en_path'])



def __get_video_file_information_from_filepath(filepath: str):
    filepath = utils.get_minio_filepath_without_bucket(filepath)
    user_id = utils.get_user_id_from_filepath(str(filepath))
    basename_result = utils.get_file_basename(filepath)
    minio_object = minio_client.get_object(filepath, user_id)
    metadata_result = ffmpeg.get_video_metadata(minio_object['file_path'])

    return {
        'user_id': user_id,
        'file_path': filepath,
        'filename': basename_result['filename'],
        'content-type': minio_object['content-type'],
        'duration': metadata_result['stream']['duration'],
        'resolution': str(metadata_result['stream']['width']) + "x" + str(metadata_result['stream']['height']),
        'extension': basename_result['extension'],
        'basename': basename_result['basename']
    }
