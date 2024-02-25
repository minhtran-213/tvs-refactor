import subprocess
import json
from config import utils
from models.responses import CommonFileResponse


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


def combine_video(video_path: str, subtitle_path: str, audio_path: str, locale_code: str):
    print("Combining video")
    dirname = utils.get_dirname(video_path)
    basename = utils.get_file_basename(video_path)['basename']
    output_path = f"{dirname}/{basename}_{locale_code}.mp4"
    combine_request = [
        'ffmpeg',
        '-i', video_path,
        '-y'
    ]

    combine_request.extend([
        '-i', audio_path,
        '-c:a', 'aac',
        '-strict', 'experimental',
        '-map', '0:v',
        '-map', '1:a',
    ])

    combine_request.extend([
        '-vf',
        f"subtitles='{subtitle_path}':force_style='Fontname=Noto Sans CJK SC,OutlineColour=&H40000000,BorderStyle=4'"
    ])

    combine_request.append(output_path)

    subprocess.run(combine_request, check=True)
    print("Combining video done")
    return CommonFileResponse(file_path=output_path, file_name=utils.get_file_basename(output_path)['filename'])


if __name__ == "__main__":
    video_paths = "/home/minhtranb/works/personal/tvs-refactor/resources/temp/123/test.mp4"
    audio_paths = '/home/minhtranb/works/personal/tvs-refactor/resources/temp/123/test_vi_vi.mp3'
    subtitle_paths = '/home/minhtranb/works/personal/tvs-refactor/resources/temp/123/test_vi.srt'
    combine_video(video_paths, subtitle_paths, audio_paths, "vi")
