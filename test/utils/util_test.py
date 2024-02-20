from config import utils


def test_when_get_file_basename_should_get_filename_dict():
    filepath = "/home/minhtranb/works/personal/tvs-refactor/resources/temp/test.mp4"
    result = utils.get_file_basename(filepath)
    assert result['basename'] == "test"
    assert result['extension'] == ".mp4"
    assert result['filename'] == "test.mp4"


def test_when_get_userid_from_filepath_should_get_userid():
    filepath = "userid_123/2024/02/18/test.mp4"
    result = utils.get_user_id_from_filepath(filepath)
    assert result == "123"


def test_when_get_minio_filepath_without_bucket_should_get_minio_filepath_without_bucket():
    filepath = "test/userid_123/2024/02/18/test.mp4"
    result = utils.get_minio_filepath_without_bucket(filepath)
    assert result == "userid_123/2024/02/18/test.mp4"
