from typing import List

from fastapi import BackgroundTasks, UploadFile
from sqlalchemy.orm import Session

from config import utils
from services import subtitle_service, locale_service
from integration.repository import video_repository
from integration.third_party import minio_client, ffmpeg, fastapi, libretranslate, tts_service
from models.entities import VideoFileStoragesEntity, LocaleEntity
from models.enums import ProcessStatus, VideoOptionRequest
from models.requests import ConvertSrtRequest, YoutubeLinkUploadRequest
from models.responses import CommonFileResponse


def process_youtube_links(background_task: BackgroundTasks,
                          db: Session,
                          youtube_request: YoutubeLinkUploadRequest):
    minio_file_path = __get_minio_file_path(str(youtube_request.user_id))
    for youtube_link in youtube_request.links:
        video_file_info = utils.download_youtube_link(youtube_link, str(youtube_request.user_id))
        saved_video_file = __save_new_video_from_youtube_info(db, str(youtube_request.user_id), video_file_info,
                                                              youtube_request.output_language)
        basename = utils.get_file_basename(video_file_info['filepath'])['basename']
        background_task.add_task(processing_video, video_file_info['filepath'], youtube_request.output_language,
                                 basename, minio_file_path, saved_video_file.id, db, str(youtube_request.user_id),
                                 youtube_request.video_option_request)


def process_uploaded_files(
        background_task: BackgroundTasks,
        db: Session,
        files: List[UploadFile],
        user_id: str,
        video_option_request: List[VideoOptionRequest],
        output_language: str
):
    __remove_duplicated_files(db, files)
    valid_file_path_list = utils.download_file_to_local(files, user_id)
    minio_file_path = __get_minio_file_path(user_id)
    for valid_file_path in valid_file_path_list:
        video_file_info = __get_video_file_information_from_filepath(valid_file_path)
        saved_video_file = __save_new_video(db, user_id, video_file_info, output_language)
        background_task.add_task(processing_video, valid_file_path, output_language, video_file_info['basename'],
                                 minio_file_path, saved_video_file.id, db, user_id, video_option_request)


def processing_video(file_path: str, locale_code: str, basename: str,
                     minio_filepath: str, video_id: int, db: Session, user_id: str,
                     video_option_request: List[VideoOptionRequest]):
    print("Processing video")
    transcribe_result = fastapi.process_srt(file_path, user_id=user_id,
                                            basename=basename, video_id=str(video_id))
    subtitle_result = __get_subtitle_results(transcribe_result, locale_code, basename)

    convert_subtitle_request = ConvertSrtRequest(code=locale_code)
    translated_audio_result = tts_service.convert_subtitles_to_audio(subtitle_result['translated_sub']['filepath'],
                                                                     convert_subtitle_request,
                                                                     user_id)
    translated_video_result = ffmpeg.combine_video(file_path, subtitle_result['translated_sub']['filepath'],
                                                   translated_audio_result.file_path, locale_code, video_option_request,
                                                   str(video_id))
    uploaded_filepath_result = __upload_files_to_minio_storage(minio_filepath, subtitle_result, translated_video_result)
    detected_language = locale_service.get_locale_by_code_like(db, transcribe_result['detected_language'])
    __update_video_info(db, video_id, uploaded_filepath_result, detected_language)
    subtitle_service.save_uploaded_subtitles(db, video_id, subtitle_result)


def __update_video_info(db: Session, video_id: int, uploaded_filepath_result: dict, detected_language: LocaleEntity):
    update_info = {
        "process_status": ProcessStatus.DONE,
        "file_path": uploaded_filepath_result['translated_video'],
        "input_locale_id": detected_language.id
    }
    db.query(VideoFileStoragesEntity).filter(VideoFileStoragesEntity.id == video_id) \
        .update(update_info)
    db.commit()


def __upload_files_to_minio_storage(minio_filepath: str, subtitle_result: dict,
                                    translated_video_result: CommonFileResponse):
    translated_subtitle_destination_path = minio_filepath + f"/{subtitle_result['translated_sub']['filename']}"
    origin_subtitle_destination_path = minio_filepath + f"/{subtitle_result['eng_sub']['filename']}"
    translated_video_destination_path = minio_filepath + f"/{translated_video_result.file_name}"
    minio_client.upload_file(translated_subtitle_destination_path, subtitle_result['translated_sub']['filepath'])
    minio_client.upload_file(origin_subtitle_destination_path, subtitle_result['eng_sub']['filepath'])
    minio_client.upload_file(translated_video_destination_path, translated_video_result.file_path)
    return {
        "translated_sub": translated_subtitle_destination_path,
        "origin_sub": origin_subtitle_destination_path,
        "translated_video": translated_video_destination_path
    }


def __get_minio_file_path(user_id: str):
    current_year = utils.get_current_date_info()['year']
    current_month = utils.get_current_date_info()['month']
    current_day = utils.get_current_date_info()['day']
    return f'{user_id}/{current_year}/{current_month}/{current_day}'


def __remove_duplicated_file(db: Session, file_name: str):
    video_file = video_repository.get_video_by_filename(db, file_name)
    if video_file:
        print(f"File {file_name} already exists")
        db.query(VideoFileStoragesEntity).filter(VideoFileStoragesEntity.id == video_file.id) \
            .update({"process_status": ProcessStatus.DUPLICATED})
        db.commit()
        return True
    return False


def __remove_duplicated_files(db: Session, file_list: List[UploadFile]):
    for file in file_list:
        current_filename = file.filename
        if __remove_duplicated_file(db, current_filename):
            file_list.remove(file)


def __save_new_video(db: Session, user_id: str, video_file_info: dict, output_language: str):
    video_file_storage = VideoFileStoragesEntity()
    locale = locale_service.get_by_code(db, output_language)
    __convert_video_information_to_entity(video_file_info, video_file_storage, locale.id)
    video_file_storage.user_id = user_id
    return video_repository.create(db, video_file_storage)


def __save_new_video_from_youtube_info(db: Session, user_id: str, video_file_info: dict, output_language: str):
    video_file_storage = VideoFileStoragesEntity()
    locale = locale_service.get_by_code(db, output_language)
    __convert_video_information_from_youtube(video_file_storage, video_file_info, locale.id)
    video_file_storage.user_id = user_id
    return video_repository.create(db, video_file_storage)


def __convert_video_information_from_youtube(video_file_storage: VideoFileStoragesEntity, youtube_info: dict,
                                             output_language_id: int):
    video_file_storage.size = youtube_info['file_size']
    video_file_storage.file_extension = youtube_info['extension']
    video_file_storage.file_name = youtube_info['title']
    video_file_storage.file_duration = youtube_info['duration']
    video_file_storage.file_resolution = youtube_info['resolution']
    video_file_storage.output_locale_id = output_language_id


def __get_video_file_information_from_filepath(filepath: str):
    basename_result = utils.get_file_basename(filepath)
    metadata_result = ffmpeg.get_video_metadata(filepath)

    return {
        'filename': basename_result['filename'],
        'duration': metadata_result['stream']['duration'],
        'resolution': str(metadata_result['stream']['width']) + "x" + str(metadata_result['stream']['height']),
        'extension': basename_result['extension'],
        'basename': basename_result['basename'],
        'size': metadata_result['format']['size']
    }


def __convert_video_information_to_entity(video_information: dict, video_file_storage: VideoFileStoragesEntity,
                                          output_locale_id: int):
    video_file_storage.file_duration = video_information['duration']
    video_file_storage.file_resolution = video_information['resolution']
    video_file_storage.file_name = video_information['filename']
    video_file_storage.process_status = ProcessStatus.PROCESSING
    video_file_storage.file_extension = video_information['extension']
    video_file_storage.size = video_information['size']
    video_file_storage.output_locale_id = output_locale_id


def __get_subtitle_results(transcribe_result, locale_code, basename):
    origin_sub_path = transcribe_result['srt_en_path']
    subtitle_path = transcribe_result['srt_en_path']
    resources_dir = utils.get_dirname(transcribe_result['srt_en_path'])
    origin_sub_filename = utils.get_file_basename(subtitle_path)['filename']
    subtitle_filename = utils.get_file_basename(subtitle_path)['filename']
    if 'en' not in locale_code:
        translated_result = libretranslate.translate_srt_file(transcribe_result['srt_en_path'],
                                                              locale_code.split('-')[0],
                                                              resources_dir + f'/{basename}_{locale_code}.srt')
        subtitle_path = translated_result.file_path
        subtitle_filename = translated_result.file_name
    return {
        "eng_sub": {
            "filename": origin_sub_filename,
            "filepath": origin_sub_path
        },
        "translated_sub": {
            "filename": subtitle_filename,
            "filepath": subtitle_path
        }
    }
