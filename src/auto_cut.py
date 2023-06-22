import concurrent.futures
import threading
import time

from moviepy.video.io.VideoFileClip import VideoFileClip

from src.analyser import get_face_many, get_face_analyser


def is_accept(frame, index, accept_infos, args):
    many_faces = get_face_many(frame)
    male_faces = [face for face in many_faces if face['gender'] == 1]
    female_faces = [face for face in many_faces if face['gender'] == 0]
    accept = args.female_min <= len(female_faces) <= args.female_max and args.male_min <= len(male_faces) <= args.male_max
    accept_infos[index] = accept
    print(f"第{index}帧结果为：{accept}")


def submit_is_accept(clip, accept_infos, args):
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        index = 0
        t = 0
        while t <= clip.duration and index < len(accept_infos):
            print(f"提交任务{index}")
            frame = clip.get_frame(t)
            executor.submit(is_accept, frame, index, accept_infos, args)
            t += args.gap_time
            index += 1


def cut_video(args):
    clip = VideoFileClip(args.input_file)
    accept_infos = [None] * int(clip.duration / args.gap_time)
    get_face_analyser()
    threading.Thread(target=submit_is_accept, args=(clip, accept_infos, args))
    time.sleep(100)

