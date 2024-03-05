import os
import pysrt
import youtube_dl
from pysrt import SubRipFile
from fastapi import UploadFile
import shutil
from datetime import datetime
from typing import List



def get_file_basename(path: str):
    filename = os.path.basename(path)
    return {
        'basename': os.path.splitext(filename)[0],
        'extension': os.path.splitext(filename)[1],
        'filename': filename
    }


def get_subtitle_file(input_path: str) -> SubRipFile:
    try:
        subs = pysrt.open(input_path, encoding='utf-8')
        return subs
    except FileNotFoundError as e:
        print(f"File not found error: {str(e)}")
    except UnicodeDecodeError as e:
        print(f"Unicode decode error: {str(e)}")


def get_dirname(path: str):
    return os.path.dirname(path)


def get_minio_filepath_without_bucket(path: str):
    filepath_components = path.split('/')[1:]
    return os.path.join(*filepath_components)


def get_user_id_from_filepath(filepath: str):
    return filepath.split("/")[0].split("_")[1]


def get_root_path():
    current_dir = os.path.dirname(__file__)
    root_dir = os.path.join(current_dir, '..')
    return os.path.abspath(root_dir)


def delete_files(path):
    print(f"Removing files in: {path}")
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        print(f"Error deleting files: {str(e)}")


def get_current_date_info():
    current_datetime = datetime.now()
    current_year = current_datetime.year
    current_month = current_datetime.month
    current_date = current_datetime.day
    return {
        'year': current_year,
        'month': current_month,
        'day': current_date
    }


def download_file_to_local(upload_file_list, user_id: str):
    upload_file_paths = []
    root_dir = get_root_path()
    for upload_file in upload_file_list:
        basename = get_file_basename(upload_file.filename)['basename']
        extension = get_file_basename(upload_file.filename)['extension']
        resources_dir = os.path.join(root_dir, "resources", user_id)
        if not os.path.exists(resources_dir):
            os.mkdir(resources_dir)
        path = os.path.join(resources_dir, f'{basename}{extension}')
        with open(path, 'w+b') as buffer:
            try:
                shutil.copyfileobj(upload_file.file, buffer)
                upload_file_paths.append(path)
            except Exception as e:
                print(f'Cannot download file to local: {e}')

    return upload_file_paths


def download_youtube_link(video_link: str, user_id: int, video_id: str):
    root_path = get_root_path()
    youtube_file = os.path.join(root_path, 'result', str(user_id), video_id, '%(title)s.%(ext)s')

    # Download video using youtube-dl with appropriate options
    ydl_opts = {
        "outtmpl": youtube_file,  # Temporary download location
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",  # Prioritize MP4 format
        "keepvideo": True,  # Keep the original video files after merging
        # ...other options based on videoOption
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_link, download=True)
            video_path = ydl.prepare_filename(info_dict)

        return {
            'file_size': os.path.getsize(video_path),
            'extension': info_dict['ext'],
            'title': info_dict['title'],
            'duration': info_dict['duration'],
            'resolution': f'{info_dict["width"]}x{info_dict["height"]}',
            'filepath': video_path
        }
    except Exception as e:
        print(f"Error downloading from youtube linK : {video_link}: {e.message}")