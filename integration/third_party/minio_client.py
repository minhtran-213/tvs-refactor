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
FILE_PATH = '/home/minhtranb/works/personal/tvs-refactor/resources/temp'


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


if __name__ == "__main__":
    print(type(get_object("/userid_123/2024/02/18/ZH1.mp4").metadata))
    print(get_object("/userid_123/2024/02/18/ZH1.mp4").metadata)
