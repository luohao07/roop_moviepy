import os
import concurrent.futures
import threading
from functools import partial

from moviepy.editor import VideoFileClip
from moviepy.video.VideoClip import DataVideoClip

from src.analyser import get_face_analyser
from src.swapper import process_frame, read_all_faces
import time
import src.globals as globals

log_level = "INFO"


# 处理帧
def handle_frame(frames, index, processed_frames, process_args):
    if globals.log_level == "DEBUG":
        print(f"开始换脸帧{index}")
    # 没值说明没有读取成功
    while frames[index] is None:
        time.sleep(0.01)
    frame = process_frame(process_args, frames[index])
    processed_frames[index] = frame
    if globals.log_level == "DEBUG":
        print(f"完成换脸帧{index}")

def handle_frames(frames, processed_frames, process_args):
    with concurrent.futures.ThreadPoolExecutor(process_args.threads) as executor:
        for index in range(len(frames)):
            executor.submit(handle_frame, frames, index, processed_frames, process_args)


# 加载帧
def extract_frames(clip, frames):
    index = 0
    for frame in clip.iter_frames():
        if index >= len(frames):
            break
        frames[index] = frame
        index += 1


def process_video(process_args):
    get_face_analyser()
    clip = VideoFileClip(process_args.input_file)
    process_args.all_faces = read_all_faces(process_args.source_imgs)
    frames = [None] * int(clip.fps * clip.duration)
    processed_frames = [None] * len(frames)

    threading.Thread(target=extract_frames, args=(clip, frames)).start()
    threading.Thread(target=handle_frames, args=(frames, processed_frames, process_args)).start()

    create_video(processed_frames, clip.fps, process_args)


def create_video(processed_frames, fps, process_args):
    print("开始合成视频")
    data = range(len(processed_frames))
    processed_clip = DataVideoClip(data=data, data_to_frame=partial(get_processed_frame, processed_frames), fps=fps)
    processed_clip.write_videofile(filename=process_args.output_file, threads=10)


def get_processed_frame(processed_frames, t):
    if globals.log_level == "DEBUG":
        print(f"获取帧{t}")
    while processed_frames[t] is None:
        time.sleep(0.01)
    processed_frame = processed_frames[t]
    if t != 0:
        processed_frames[t] = None
    if globals.log_level == "DEBUG":
        print(f"返回帧{t}")
    return processed_frame


def main(process_args):
    assert os.path.exists(process_args.input_file)
    globals.log_level = process_args.log_level
    for source_img in process_args.source_imgs:
        assert os.path.exists(source_img)
    if process_args.input_file and process_args.output_file:
        process_video(process_args)
    else:
        print('Please provide both input and output file paths.')
