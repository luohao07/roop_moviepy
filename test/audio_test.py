from moviepy.video.io.VideoFileClip import VideoFileClip


def cut_with_audio(args):
    clip = VideoFileClip(args.input_file)
    video_sub_clip = clip.subclip(1, 10)
    audio_sub_clip = clip.audio.subclip(1, 10)

    video_sub_clip.set_audio(audio_sub_clip)

    video_sub_clip.write_videofile(args.input_file)
