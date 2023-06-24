from moviepy.video.io.VideoFileClip import VideoFileClip


def cut_with_audio(args):
    clip = VideoFileClip(args.input_file)
    video_sub_clip = clip.subclip(100, 150)
    audio_sub_clip = clip.audio.subclip(100, 150)

    video_sub_clip.set_audio(audio_sub_clip)

    video_sub_clip.write_videofile(args.output_file)
