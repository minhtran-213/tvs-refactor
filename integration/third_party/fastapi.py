from typing import Optional

from faster_whisper import WhisperModel
import torch
import os

device = "cuda" if torch.cuda.is_available() else "cpu"
compute_type = "float16" if device == "cuda" else "int8"
print(device)
model = WhisperModel("medium", device="cpu", compute_type="int8")


def process_srt(file_path: str, user_id: str, basename: str, task: Optional[str] = "translate"):
    transcribe_result = __transcribe(file_path, task)
    if not transcribe_result:
        print("Cannot transcribe")
        return
    srt_full_path = __convert_to_srt(transcribe_result['transcribe_chunk'], basename, user_id)
    return {
        "srt_en_path": srt_full_path,
        "detected_language": transcribe_result['detected_language'] if transcribe_result['detected_language'] else "en"
    }


def __transcribe(file_path: str, task: Optional[str]):
    print("Transcribing")
    try:
        if not os.path.exists(file_path):
            print(f"File path {file_path} not found")
        transcribe_result = model.transcribe(file_path, beam_size=5, word_timestamps=True, task=task)
        print("Transcribing finished")
        return {
            'transcribe_chunk': transcribe_result[0],
            'detected_language': transcribe_result[1].language
        }
    except Exception as e:
        print(f"Transcribing audio failed: {e}")


def __convert_to_srt(translate_result, filename, user_id: str):
    print("Converting to SRT")
    srt_full_path = f'../../resources/temp/{user_id}/{filename}_en.srt'
    with open(srt_full_path, "w") as file:
        sentence = []
        start_time = None
        counter = 1
        for segment in translate_result:
            for word in segment.words:
                if not sentence:
                    start_time = word.start
                sentence.append(word.word)
                end_time = word.end
                if word.word.endswith((',', '.')):
                    file.write(f"{counter}\n")
                    file.write(f"{__format_timestamp(start_time)} --> {__format_timestamp(end_time)}\n")
                    file.write(f"{' '.join(sentence)}\n\n")
                    sentence = []
                    start_time = None
                    counter += 1
    print("Converting to SRT finished")
    return srt_full_path


def __format_timestamp(seconds):
    """Convert seconds to timestamp format for SRT."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02},{int((seconds - int(seconds)) * 1000):03}"


if __name__ == "__main__":
    file_paths = '/home/minhtranb/works/personal/tvs-refactor/resources/temp/test.mp4'
    result = process_srt(file_paths, "translate")
    print(result)
