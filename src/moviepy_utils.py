import os.path
from moviepy.tools import find_extension


def save_clip_audio(clip, video_filename, audio_codec='aac'):
    name, ext = os.path.splitext(video_filename)
    audio_ext = find_extension(audio_codec)

    audiofile = (name + "TEMP_MPY_wvf_snd.mp3")
    clip.audio.write_audiofile(audiofile, nbytes=4)
    return audiofile
