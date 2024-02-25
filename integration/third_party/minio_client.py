from minio import Minio
from minio.error import S3Error
from config import utils
import os

minio_client = Minio(
    endpoint="localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

BUCKET_NAME = "test"
FILE_PATH = '../../resources/temp'


def get_object(object_name: str, user_id: str):
    try:
        destination_path = os.path.join(FILE_PATH, user_id, "test.mp4")
        file_object = minio_client.fget_object(BUCKET_NAME, object_name, destination_path)
        return {
            'content-type': file_object.metadata['Content-Type'],
            'file_path': destination_path
        }
    except S3Error as e:
        print(f"Error occurred when getting object: {e}")
    except Exception as e:
        print(f"Error occurred when getting object: {e}")


def upload_file(object_name: str, file_path: str):
    print(f"Saving to S3 Storage with filepath: {file_path}")
    try:
        minio_client.fput_object(bucket_name=BUCKET_NAME, object_name=object_name, file_path=file_path)
        print("File saved")
    except S3Error as e:
        print(f"S3 error when uploading bucket: {e}")
        return
    except Exception as e:
        print(f"S3 error when uploading bucket: {e}")


if __name__ == "__main__":
    upload_file("/userid_123/2024/02/18/test_vi.mp4", "/home/minhtranb/works/personal/tvs-refactor/resources/temp/123/test_vi.mp4")
