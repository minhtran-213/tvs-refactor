import subprocess
import json


def get_video_metadata(video_path: str):
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        video_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        metadata = json.loads(result.stdout)
        h264_item = next((item for item in metadata['streams'] if item['codec_name'] == "h264"), None)
        return {
            'stream': h264_item,
            'format': metadata['format'],
        }
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip()
        print(f"ffprobe error output: {error_message}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")


if __name__ == "__main__":
    video_path = "/home/minhtranb/works/personal/tvs-refactor/resources/temp/test.mp4"
    result = get_video_metadata(video_path)
    print(result)
