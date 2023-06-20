import argparse
import os
import concurrent.futures
import queue

from moviepy.editor import VideoFileClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

from src.analyser import get_face_analyser
from src.swapper import process_frame, read_all_faces
from tqdm import tqdm

import concurrent.futures

import concurrent.futures
import threading


def handle_frame(frame, index, processed_frames, progress, process_args, lock):
    processed_frame = process_frame(process_args, frame, progress)
    with lock:
        processed_frames[index] = processed_frame


def process_video(process_args):
    get_face_analyser()
    clip = VideoFileClip(process_args.input_file)
    progress = tqdm(total=int(clip.fps * clip.duration))
    processed_frames = [None] * len(clip)

    process_args.all_faces = read_all_faces(process_args.source_imgs)

    # 创建线程池和锁
    with concurrent.futures.ThreadPoolExecutor(max_workers=process_args.threads) as executor:
        lock = threading.Lock()

        # 提交任务并获取Future对象
        futures = [
            executor.submit(
                handle_frame,
                frame,
                index,
                processed_frames,
                progress,
                process_args,
                lock
            )
            for index, frame in enumerate(clip.iter_frames())
        ]

        # 等待所有任务完成
        concurrent.futures.wait(futures)

    print("reface finished")
    print(processed_frames)
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

