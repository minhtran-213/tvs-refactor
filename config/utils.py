import os
import pysrt
from pysrt import SubRipFile
import shutil


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
    root_dir = os.path.join(current_dir, '..', '..')
    return os.path.abspath(root_dir)


def delete_files(path):
    print(f"Removing files in: {path}")
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        print(f"Error deleting files: {str(e)}")
