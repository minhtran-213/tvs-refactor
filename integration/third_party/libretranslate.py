import requests
from requests import HTTPError, Timeout

def __read_text_from_srt_file(srt_path):
        with open(srt_path, "r") as f:
            content = f.readlines()
        subtitles = []
        subtitle_list = []
        for line in content:
            if line.strip().isdigit() and subtitle_list:
                subtitles.append(__parse_subtitle_block(subtitle_list))
                subtitle_list = []
            subtitle_list.append(line.strip())
        if subtitle_list:
            subtitles.append(__parse_subtitle_block(subtitle_list))
        return subtitles

def __translate(subtitles, destination_language):
    endpoint = "http://localhost:8000/translate"
    
    for subtitle in subtitles:
        param = {"q": subtitle.text, "source": "en", "target": destination_language, "format": "text"}
        try:
            response = requests.post(endpoint, params=param)
            if response.status_code == 200:
                json = response.json()
                return json['translatedText']
            else:
                json_data = response.json()
                print(f"TRANSLATING ERROR RESPONSE: {json_data}")
        except HTTPError as e:
            print(f"Http request to Libre Translating failed: {e}")
            return
        except Timeout as e:
            print(f"Http request to Libre Translating timeout failed: {e}")
            return
        except ConnectionError as e:
            print(f"Http request to Libre Translating connection failed: {e}")
            return
        except Exception as e:
            print(f"Http request to Libre Translating failed: {e}")
            return


def __parse_subtitle_block(block):
    number = block[0]
    time_code = block[1]
    text = ' '.join(block[2:])
    return {
        'number': number,
        'time_code': time_code,
        'text': text
    }

def translate_srt_into_language(srt_path: str, destination_language: str, output_destination: str):
    print("Start translating")
    subtitles = __read_text_from_srt_file(srt_path)
    translate_result = __translate("")