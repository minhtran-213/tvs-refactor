import os


def get_file_basename(path: str):
    filename = os.path.basename(path)
    return {
        'basename': os.path.splitext(filename)[0],
        'extension': os.path.splitext(filename)[1],
        'filename': filename
    }


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
