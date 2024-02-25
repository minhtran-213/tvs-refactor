from gtts import gTTS
from config import utils
from moviepy.editor import concatenate_audioclips, AudioFileClip, vfx
from moviepy.audio.AudioClip import AudioClip
from models.requests import ConvertSrtRequest
import os


class ConvertSsmlToAudioException(Exception):
    def __init__(self, message=None):
        if message:
            self.message = f"ConvertSsmlToAudioException - {message}"
        else:
            self.message = "ConvertSsmlToAudioException - Unknown error occurs"
        super().__init__(self.message)


def convert_text_to_audio_using_gtts(text, filename, lang):
    try:
        speech = gTTS(text, lang)
        speech.save(filename)
    except Exception as e:
        raise ValueError(f'Translating google failed: {str(e)}')


def __subrip_to_milliseconds(subrip_time):
    return (subrip_time.hours * 3600000) + (subrip_time.minutes * 60000) + (
            subrip_time.seconds * 1000) + subrip_time.milliseconds


def convert_subtitles_to_audio(origin_sub_path: str, convert_request: ConvertSrtRequest):
    subs = utils.get_subtitle_file(origin_sub_path)

    audio_clips = []
    timeline = 0  # This is to hold the current timeline

    origin_path = os.path.dirname(origin_sub_path)

    try:
        for i in range(len(subs)):
            sub = subs[i]
            text = sub.text.replace('\n', ' ')

            subtitle_info = __get_subtitle_info(sub)

            # Calculate silence duration based on the current timeline position
            silence_duration = (subtitle_info['start'] - timeline) / 1000.0
            silence_duration = round(silence_duration, 3)
            if silence_duration > 0:
                silence_clip = AudioClip(lambda t: [0, 0], duration=silence_duration)
                audio_clips.append(silence_clip)
                timeline += silence_duration * 1000  # Update timeline

            temp_dir = os.path.join(origin_path, 'temp')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)

            audio_filename = os.path.join(temp_dir, f'temp_{i}.mp3')
            if convert_request.code:
                print("Using gtts library to generate audio")
                convert_text_to_audio_using_gtts(text=text, filename=audio_filename, lang=convert_request.code)

            audio_clip = AudioFileClip(audio_filename)
            audio_duration = audio_clip.duration * 1000

            # Check if the next subtitle starts after the current audio ends
            next_sub_start = __subrip_to_milliseconds(subs[i + 1].start) if i + 1 < len(subs) else None
            if next_sub_start and next_sub_start > timeline + audio_duration:
                # Do not speed up the audio if it does not overlap with the next subtitle
                pass
            elif audio_duration > subtitle_info['duration'] != 0:
                # Speed up the audio if it overlaps with the next subtitle
                print(f"Current duration: {subtitle_info['duration']}")
                speed_ratio = audio_duration / subtitle_info['duration']
                audio_clip = audio_clip.fx(vfx.speedx, speed_ratio)
                audio_duration = subtitle_info['duration']  # Update audio_duration after speed change

            audio_clips.append(audio_clip)
            timeline += audio_duration  # Update timeline

        final_audio = concatenate_audioclips(audio_clips)

        # Create the output filename based on the input filename
        srt_basename = os.path.basename(origin_sub_path)
        srt_name, _ = os.path.splitext(srt_basename)
        output_filename = os.path.join(origin_path, f'{srt_name}_{convert_request.code}.mp3')
        final_audio.write_audiofile(output_filename, bitrate='184k')
        return output_filename
    except Exception as e:
        print(f"Converting srt to audio failed: {str(e)}")
        raise ConvertSsmlToAudioException(e)


def __get_subtitle_info(sub):
    start = __subrip_to_milliseconds(sub.start)
    end = __subrip_to_milliseconds(sub.end)
    return {
        "start": start,
        "end": end,
        "duration": end - start
    }


if __name__ == "__main__":
    srt_path = '/home/minhtranb/works/personal/tvs-refactor/resources/temp/test_vi.srt'
    convert_requests = ConvertSrtRequest(code='en')
    convert_subtitles_to_audio(srt_path, convert_requests)
    print("Done!")
