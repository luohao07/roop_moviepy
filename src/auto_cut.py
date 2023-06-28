import concurrent.futures
import json
import os
import shutil
import time

from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from tqdm import tqdm

from src.analyser import get_face_many, get_face_analyser


def get_index_range(arr, accept_min_size):
    ranges = []
    start = None

    for i, value in enumerate(arr):
        if value is None:
            continue
        if value:
            if start is None:
                start = i
        else:
            if start is not None:
                ranges.append([start, i - 1])
                start = None

    if start is not None:
        ranges.append([start, len(arr) - 1])

    accept_range = []
    for _range in ranges:
        s, e = _range
        # print(f"{_range}，时长为{e-s+1}，需要时长为{accept_min_size}")
        if e - s + 1 >= accept_min_size:
            accept_range.append(_range)

    return accept_range


def is_accept(frame, index, accept_infos, progress, args):
    many_faces = get_face_many(frame)
    male_faces = [face for face in many_faces if face['gender'] == 1]
    female_faces = [face for face in many_faces if face['gender'] == 0]
    accept = args.female_min <= len(female_faces) <= args.female_max and args.male_min <= len(
        male_faces) <= args.male_max
    accept_infos[index] = accept
    progress.update(1)


def copy_input_file(args):
    basename = os.path.basename(args.input_file)
    name, extension = os.path.splitext(basename)
    files = [args.input_file]
    # for index in range(args.copies):
    #     copy_file_path = f"{os.path.dirname(args.input_file)}/{name}_copy{index}{extension}"
    #     if os.path.exists(copy_file_path):
    #         print("第{index}个文件已存在，跳过")
    #         files.append(copy_file_path)
    #         continue
    #     shutil.copy(args.input_file, copy_file_path)
    #     print(f"复制第{index}个文件成功：{copy_file_path}")
    #     files.append(copy_file_path)
    return files * args.copies


def init_gap_times(args, frame_size):
    if not args.gap_times or len(args.gap_times) == 0:
        if frame_size > 10 * 10000:
            args.gap_times = [2, 0.4, 0.08, 0]
        elif frame_size > 3 * 10000:
            args.gap_times = [0.8, 0.1, 0]
        elif frame_size > 1 * 10000:
            args.gap_times = [0.4, 0]
        else:
            args.gap_times = [0]
        print(f"自动选择gap_times完毕{args.gap_times}")


def count_frame(accept_infos):
    return {
        "accept": accept_infos.count(True),
        "deny": accept_infos.count(False),
        "uncheck": accept_infos.count(None)
    }


def set_false_out_times(accept_infos, clip, args):
    if not (args.min_time or args.max_time):
        args.min_time = 0
        args.max_time = clip.duration
        return

    if not args.min_time:
        args.min_time = 0

    if not args.max_time:
        args.max_time = clip.duration

    for index in range(len(accept_infos)):
        t = index * 1.0 / clip.fps
        if t < args.min_time or t > args.max_time:
            accept_infos[index] = False


def cut_video_wrap(args):
    files = copy_input_file(args)
    print(files)
    cut_start_time = time.perf_counter()
    clips = []
    for file in files:
        clips.append(VideoFileClip(file))

    accept_infos = [None] * int(clips[0].duration * clips[0].fps)
    set_false_out_times(accept_infos, clips[0], args)
    init_gap_times(args, accept_infos.count(None))

    get_face_analyser()
    for index, gap_time in enumerate(args.gap_times):
        if gap_time < 1.0 / clips[0].fps:
            gap_time = 1.0 / clips[0].fps
            print(f"gap time 过低，重置为1/fps={gap_time}")
        progress = tqdm((args.max_time - args.min_time) * clips[0].fps / gap_time)
        print(progress.total)
        print(f"开始第{index}轮剪辑gap_time={gap_time}，当前待检测帧{accept_infos.count(None)}，",
              f"已过滤帧{accept_infos.count(False)}, 已接受帧{accept_infos.count(True)}")
        args.gap_time = gap_time
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(clips)) as executor:
            for task_i in range(len(clips)):
                start_time = (args.max_time - args.min_time) / len(clips) * task_i + args.min_time
                end_time = (args.max_time - args.min_time) / len(clips) * (task_i + 1) + args.min_time
                print(f"提交第{index}轮第{task_i + 1}个任务，start_time={start_time}, end_time = {end_time}")
                executor.submit(cut_video, clips[task_i], accept_infos, args, start_time, end_time, progress)
        # 如果任意两个时间差小于accept_min_time的帧都为False，那中间的部分就不用检测了，直接设置为False
        print(f"第{index}轮执行完成")
        set_false_between(accept_infos, args.accept_min_time * clips[0].fps)

    cut_frames = get_index_range(accept_infos, args.accept_min_time * clips[0].fps)
    for arr in cut_frames:
        for i in range(len(arr)):
            arr[i] = arr[i] * 1.0 / clips[0].fps
    cut_times = cut_frames

    try:
        new_clip = do_cut_to_clip(clips[0], args, cut_times)
        new_clip.write_videofile(args.output_file, threads=args.threads * args.copies, audio_codec='aac')
    except:
        print(f"合成失败！文件占用，现场已保存，可使用以下命令重试合成操作: ",
              f"python repay_cut.py --i {args.input_file} -o {args.output_file} -f {args.input_file}.txt")
    print(f"剪辑完成，共计耗时: {time.perf_counter() - cut_start_time}")


def set_false_between(array, min_size):
    false_indices = [i for i, val in enumerate(array) if val is False]

    for i in range(len(false_indices) - 1):
        if false_indices[i + 1] - false_indices[i] - 1 <= min_size:
            start_index = false_indices[i]
            end_index = false_indices[i + 1]
            for j in range(start_index + 1, end_index):
                array[j] = False

    return array


def cut_video(clip, accept_infos, args, start_time, end_time, progress):
    print(f"开始执行任务[{start_time}, {end_time}]")

    fail_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        t = start_time
        index = int(t * clip.fps)
        while t <= end_time and index < len(accept_infos):
            if accept_infos[index] is None:
                try:
                    frame = clip.get_frame(t)
                    executor.submit(is_accept, frame, index, accept_infos, progress, args)
                except:
                    print(f"第{index}帧读取失败")
                    accept_infos[index] = False
                    fail_count += 1
                    if fail_count >= 10:
                        break
            else:
                progress.update(1)
            t += args.gap_time
            index = int(t * clip.fps)


def do_cut_to_clip(clip, args, cut_times, save_log = True):
    sub_clips = []
    sum_time = 0
    if save_log:
        with open(f"{args.input_file}.txt", 'w') as file:
            cut_info = {
                "cut_times": cut_times
            }
            file.write(json.dumps(cut_info))
    for cut_time in cut_times:
        s, e = cut_time
        sum_time += e - s
        try:
            sc = clip.subclip(s, e)
            sc = sc.set_audio(clip.audio.subclip(s, e))
            sub_clips.append(sc)
        except:
            print(f"提取片段时出现异常，片段:[{s}, {e}],")
            continue

    print(f"原时间:{clip.duration}，剪辑后的时长:{sum_time}")
    return concatenate_videoclips(sub_clips)
