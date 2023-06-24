import argparse

from moviepy.video.io.VideoFileClip import VideoFileClip


def cut_with_audio(input_file, output_file):
    clip = VideoFileClip(input_file)
    video_sub_clip = clip.subclip(100, 150)
    video_sub_clip = video_sub_clip.set_audio(clip.audio.subclip(100, 150))
    video_sub_clip.write_videofile(output_file, codec='libx264', audio_codec='aac')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video processing using MoviePy')
    parser.add_argument('-i', '--input_file', type=str, help='Input video file')
    parser.add_argument('-o', '--output_file', type=str, help='Output video file')
    args = parser.parse_args()
    cut_with_audio(args.input_file, args.output_file)
