import requests
from requests import HTTPError, Timeout
from config import utils

from models.responses import CommonFileResponse


class TranslateSrtToLanguageException(Exception):
    def __init__(self, message=None):
        super().__init__(f"TranslateSrtToLanguageException - {message or 'Unknown error occurs'}")


def translate_srt_file(srt_path, destination_language, output_path):
    print(f"Translating subtitles to {destination_language}")
    subtitles = __read_text_from_srt_file(srt_path)
    for subtitle in subtitles:
        translated_text = __translate_text(subtitle['text'], destination_language)
        subtitle['text'] = translated_text
    __write_text_to_srt(subtitles, output_path)
    print("Translation done")
    return CommonFileResponse(file_path=output_path, file_name=utils.get_file_basename(output_path)['filename'])


def __parse_subtitle_block(block):
    number = block[0]
    time_code = block[1]
    text = ' '.join(block[2:])
    return {'number': number, 'time_code': time_code, 'text': text}


# Reading SRT File
def __read_text_from_srt_file(srt_path):
    subtitles = []
    with open(srt_path, "r") as f:
        content = f.readlines()
    subtitle = []
    for line in content:
        if line.strip().isdigit() and subtitle:
            subtitles.append(__parse_subtitle_block(subtitle))
            subtitle = []
        subtitle.append(line.strip())
    if subtitle:
        subtitles.append(__parse_subtitle_block(subtitle))
    return subtitles


# API Call to Translate
def __translate_text(text, destination_language):
    api = "http://localhost:5000/translate"
    param = {"q": text, "source": "en", "target": destination_language, "format": "text"}
    try:
        response = requests.post(api, params=param)
        response.raise_for_status()
        return response.json().get('translatedText', '')
    except (HTTPError, Timeout, ConnectionError) as e:
        print(f"HTTP request failed: {e}")
        raise TranslateSrtToLanguageException(str(e))


# Writing to SRT
def __write_text_to_srt(subtitles, output_path):
    with open(output_path, "w", encoding='utf-8') as f:
        for subtitle in subtitles:
            f.write(f"{subtitle['number']}\n")
            f.write(f"{subtitle['time_code']}\n")
            f.write(f"{subtitle['text']}\n\n")


if __name__ == "__main__":
    translate_srt_file("../../resources/temp/123/test_en.srt", "vi", "../../resources/temp/123/test_vi.srt")
    print("Translation done")
