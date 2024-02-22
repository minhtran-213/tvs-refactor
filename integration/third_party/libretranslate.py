import requests
from requests import HTTPError, Timeout


def translate(destination_language, subtitles):
    endpoint = "http://localhost:8000/translate"
    for subtitle in subtitles:
        param = {"q": subtitle.text, "source": "en", "target": destination_language, "format": "text"}
        try:
            response = requests.post(endpoint, params=param)
            if response.status_code == 200:
                json = response.json()
                subtitle.text = json['translatedText']
                confidence.append(0)
            else:
                json_data = response.json()
                print(f"TRANSLATING ERROR RESPONSE: {json_data}")
        except HTTPError as e:
            print(f"Http request to Libre Translating failed: {e}")
        except Timeout as e:
            logging.warning(f"Http request to Libre Translating timeout failed: {e}")
            raise TranslateSrtToLanguageException(e)
        except ConnectionError as e:
            logging.warning(f"Http request to Libre Translating connection failed: {e}")
            raise TranslateSrtToLanguageException(e)
        except Exception as e:
            logging.warning(f"Http request to Libre Translating failed: {e}")
            raise TranslateSrtToLanguageException(e)
