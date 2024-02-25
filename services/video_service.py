from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from config import utils
from models.entities import VideoFileStoragesEntity
from models.requests import MinIORequest, ConvertSrtRequest
from models.enums import ProcessStatus
from integration.third_party import minio_client, ffmpeg, fastapi, libretranslate, tts_service
from services import locale_service


def handle_minio_notification(db: Session, minio_request: MinIORequest, background_tasks: BackgroundTasks):
    video_file_storage: VideoFileStoragesEntity = MinIORequest.convert_to_video_file_storage_entity(minio_request)
    video_information = __get_video_file_information_from_filepath(minio_request.key)
    if video_information['extension'] in ['mp4', 'mov']:
        print("Extension not supported!")
        return
    video_file_storage = __convert_video_information_to_entity(video_information, video_file_storage)

    locale_code = video_information['basename'].split("_")[1]
    locale = locale_service.get_by_code(db, locale_code)
    if not locale:
        print(f"Locale {locale_code} not found")
        return
    video_file_storage.output_locale_id = locale.id

    db.add(video_file_storage)
    db.commit()

    background_tasks.add_task(processing_video, video_information['file_path'], locale_code, video_information,
                              minio_request.key)
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


def processing_video(file_path: str, locale_code: str, video_file_information: dict, minio_filepath: str):
    print("Processing video")
    basename = video_file_information['basename']
    transcribe_result = fastapi.process_srt(file_path, user_id=video_file_information['user_id'],
                                            basename=basename)
    subtitle_result = __get_subtitle_results(transcribe_result, locale_code, basename)

    convert_subtitle_request = ConvertSrtRequest(code=locale_code)
    translated_audio_result = tts_service.convert_subtitles_to_audio(subtitle_result['subtitle_filepath'],
                                                                     convert_subtitle_request,
                                                                     video_file_information['user_id'])
    translated_video_result = ffmpeg.combine_video(file_path, subtitle_result['subtitle_filepath'],
                                                   translated_audio_result.file_path, locale_code)
    minio_dirname = utils.get_dirname(utils.get_minio_filepath_without_bucket(minio_filepath))
    minio_client.upload_file(minio_dirname.join(f"/{subtitle_result['subtitle_filename']}"),
                             subtitle_result['subtitle_filepath'])
    minio_client.upload_file(minio_dirname.join(f"/{translated_video_result.file_name}"),
                             translated_video_result.file_path)


def __get_subtitle_results(transcribe_result, locale_code, basename):
    subtitle_path = transcribe_result['srt_en_path']
    resources_dir = utils.get_dirname(transcribe_result['srt_en_path'])
    subtitle_filename = utils.get_file_basename(subtitle_path)['filename']
    if 'en' not in locale_code:
        translated_result = libretranslate.translate_srt_file(transcribe_result['srt_en_path'], locale_code,
                                                              resources_dir + f'/{basename}_{locale_code}.srt')
        subtitle_path = translated_result.file_path
        subtitle_filename = translated_result.file_name
    return {
        "subtitle_filename": subtitle_filename,
        "subtitle_filepath": subtitle_path
    }


def __get_video_file_information_from_filepath(minio_filepath: str):
    filepath = utils.get_minio_filepath_without_bucket(minio_filepath)
    user_id = utils.get_user_id_from_filepath(str(filepath))
    basename_result = utils.get_file_basename(filepath)
    minio_object = minio_client.get_object(filepath, user_id)
    metadata_result = ffmpeg.get_video_metadata(minio_object['file_path'])

    return {
        'user_id': user_id,
        'file_path': minio_object['file_path'],
        'filename': basename_result['filename'],
        'content-type': minio_object['content-type'],
        'duration': metadata_result['stream']['duration'],
        'resolution': str(metadata_result['stream']['width']) + "x" + str(metadata_result['stream']['height']),
        'extension': basename_result['extension'],
        'basename': basename_result['basename']
    }
