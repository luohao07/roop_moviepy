import argparse
import os
from functools import partial

from moviepy.editor import VideoFileClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

from src.swapper import process_frame
from tqdm import tqdm


def handle_frame(frame, progress, process_args):
    frame = process_frame(process_args, frame, progress)
    return frame


def process_video(process_args):
    clip = VideoFileClip(process_args.input_file)
    progress = tqdm(total=int(clip.fps * clip.duration))
    processed_frames = []
    for frame in clip.iter_frames():
        processed_frame = handle_frame(frame, progress, process_args)
        processed_frames.append(processed_frame)
        if len(processed_frames) > 10:
            break

    processed_clip = ImageSequenceClip(processed_frames, durations=[1/clip.fps] * len(processed_frames), fps=clip.fps)
    processed_clip.write_videofile(process_args.output_file)
    progress.close()


def main(process_args):
    assert os.path.exists(process_args.input_file)
    for source_img in process_args.source_imgs:
        assert os.path.exists(source_img)
    if process_args.input_file and process_args.output_file:
        process_video(process_args)
    else:
        print('Please provide both input and output file paths.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video processing using MoviePy')
    parser.add_argument('-i', '--input_file', type=str, help='Input video file')
    parser.add_argument('-o', '--output_file', type=str, help='Output video file')
    parser.add_argument('-f', '--source_imgs', nargs='+', type=str, help='Image file paths')
    args = parser.parse_args()
    main(args)
