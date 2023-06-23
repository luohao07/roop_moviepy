import argparse
import json

from moviepy.video.io.VideoFileClip import VideoFileClip

from src.auto_cut import do_cut_to_clip
from src.core import main

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video processing using MoviePy')
    parser.add_argument('-i', '--input_file', type=str, help='Input video file')
    parser.add_argument('-o', '--output_file', type=str, help='Output video file')
    parser.add_argument('-f', '--log_file', nargs='+', type=str, help='log_file')
    args = parser.parse_args()

    with open(args.log_file,"r") as file:
        clip = VideoFileClip(args.input_file)
        log = json.load(file)
        do_cut_to_clip(clip, args, log['cut_times'], False)