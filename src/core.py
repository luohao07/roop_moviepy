import os
import concurrent.futures
import threading
from functools import partial

from moviepy.editor import VideoFileClip
from moviepy.video.VideoClip import DataVideoClip

from src.analyser import get_face_analyser
from src.moviepy_utils import save_clip_audio
from src.swapper import process_frame, read_all_faces
import time
import src.globals as globals

wait_times = [0, 0]


# 处理帧
def handle_frame(frames, index, processed_frames):
    if globals.args.log_level == "DEBUG":
        print(f"开始换脸帧{index}")
    # 没值说明没有读取成功
    while frames[index] is None:
        wait_times[0] += 1
        time.sleep(globals.args.sleep_time)
    try:
        frame = process_frame(frames[index])
    except Exception as e:
        print(e)
        frame = frames[index]
    frames[index] = None  # 释放内存
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
        if index % globals.args.max_cache_frames == 0:
            # 每加载完200帧，检查一下待处理的数量，太多了就暂停一会
            while True:
                wait_frame_count = 0
                for f in frames:
                    if f is not None:
                        wait_frame_count += 1
                if wait_frame_count >= globals.args.max_cache_frames:
                    time.sleep(2)
                else:
                    break
        index += 1
    print("extract finish!")


def print_info(frames, processed_frames):
    while True:
        try:
            wait_frame_count = 0
            for f in frames:
                if f is not None:
                    wait_frame_count += 1

            wait_write_count = 0
            for f in processed_frames:
                if f is not None:
                    wait_write_count += 1

            print(f"等待次数：{wait_times}，等待处理数量{wait_frame_count}, 等待写入数量{wait_write_count}")
        except Exception as e:
            print(e)
            pass
        time.sleep(5)


def process_video():
    start_time = time.perf_counter()
    clip = VideoFileClip(globals.args.input_file)
    frames = [None] * int(clip.fps * clip.duration)
    processed_frames = [None] * len(frames)

    get_face_analyser()
    globals.args.all_faces = read_all_faces(globals.args.source_imgs)
    audio_file = save_clip_audio(clip, video_filename=globals.args.input_file)

    threading.Thread(target=print_info, args=(frames, processed_frames)).start()
    threading.Thread(target=extract_frames, args=(clip, frames)).start()
    threading.Thread(target=handle_frames, args=(frames, processed_frames)).start()

    create_video(processed_frames, clip, audio_file)
    print(f"处理完成，耗时{time.perf_counter() - start_time}")


def create_video(processed_frames, clip, audio_file):
    data = range(len(processed_frames))
    processed_clip = DataVideoClip(data=data, data_to_frame=partial(get_processed_frame, processed_frames),
                                   fps=clip.fps)
    processed_clip = processed_clip.set_audio(clip.audio)
    processed_clip.write_videofile(filename=globals.args.output_file, threads=globals.args.threads, audio_codec='aac',
                                   audio=audio_file)


def get_processed_frame(processed_frames, index):
    if globals.args.log_level == "DEBUG":
        print(f"获取帧{index}")
    while processed_frames[index] is None:
        wait_times[0] += 1
        time.sleep(globals.args.sleep_time)
    processed_frame = processed_frames[index]
    # 这里是释放内存，获取index+1时说明index帧已经处理完了
    if index >= 1:
        processed_frames[index - 1] = None
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
