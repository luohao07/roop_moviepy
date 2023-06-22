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


# 处理帧
def handle_frame(frames, index, processed_frames):
    if globals.args.log_level == "DEBUG":
        print(f"开始换脸帧{index}")
    # 没值说明没有读取成功
    while frames[index] is None:
        time.sleep(0.01)
    try:
        frame = process_frame(frames[index])
    except Exception as e:
        print(e)
        frame = frames[index]
    processed_frames[index] = frame
    if globals.args.log_level == "DEBUG":
        print(f"完成换脸帧{index}")


def handle_frames(frames, processed_frames):
    with concurrent.futures.ThreadPoolExecutor(globals.args.threads) as executor:
        for index in range(len(frames)):
            executor.submit(handle_frame, frames, index, processed_frames)


# 加载帧
def extract_frames(clip, frames):
    index = 0
    for frame in clip.iter_frames():
        if index >= len(frames):
            break
        frames[index] = frame
        index += 1


def process_video():
    get_face_analyser()
    clip = VideoFileClip(globals.args.input_file)
    globals.args.all_faces = read_all_faces(globals.args.source_imgs)
    frames = [None] * int(clip.fps * clip.duration)
    processed_frames = [None] * len(frames)

    threading.Thread(target=extract_frames, args=(clip, frames)).start()
    threading.Thread(target=handle_frames, args=(frames, processed_frames)).start()

    create_video(processed_frames, clip)


def create_video(processed_frames, clip):
    data = range(len(processed_frames))
    processed_clip = DataVideoClip(data=data, data_to_frame=partial(get_processed_frame, processed_frames), fps=clip.fps)
    processed_clip = processed_clip.set_audio(clip.audio)
    processed_clip.write_videofile(filename=globals.args.output_file, threads=globals.args.threads)


def get_processed_frame(processed_frames, t):
    if globals.args.log_level == "DEBUG":
        print(f"获取帧{t}")
    while processed_frames[t] is None:
        time.sleep(0.01)
    processed_frame = processed_frames[t]
    if t >= 3:
        processed_frames[t-3] = None
    if globals.args.log_level == "DEBUG":
        print(f"返回帧{t}")
    return processed_frame


def main(args):
    assert os.path.exists(args.input_file)
    globals.args = args
    globals.args.log_level = args.log_level
    for source_img in args.source_imgs:
        assert os.path.exists(source_img)
    if args.input_file and args.output_file:
        process_video()
    else:
        print('Please provide both input and output file paths.')
