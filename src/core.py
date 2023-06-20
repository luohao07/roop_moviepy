import argparse
import os
import concurrent.futures
import queue

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

    # 创建有序队列
    processed_queue = queue.Queue()

    # 创建线程池
    with concurrent.futures.ThreadPoolExecutor(max_workers=process_args.threads) as executor:
        frame_infos = [(frame, progress, process_args) for frame in clip.iter_frames()]
        # 使用多线程处理帧，并将处理后的帧放入队列
        executor.map(processed_queue.put, executor.map(handle_frame, frame_infos))

    # 从队列中按顺序取出处理后的帧
    while not processed_queue.empty():
        processed_frames.append(processed_queue.get())

    processed_clip = ImageSequenceClip(processed_frames, durations=[1/clip.fps] * len(processed_frames), fps=clip.fps)
    processed_clip.write_videofile(process_args.output_file, threads=process_args.threads)
    progress.close()


def main(process_args):
    assert os.path.exists(process_args.input_file)
    for source_img in process_args.source_imgs:
        assert os.path.exists(source_img)
    if process_args.input_file and process_args.output_file:
        process_video(process_args)
    else:
        print('Please provide both input and output file paths.')

