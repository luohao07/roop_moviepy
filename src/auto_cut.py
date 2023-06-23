import concurrent.futures
import json

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


def cut_video_wrap(args):
    clip = VideoFileClip(args.input_file)
    accept_infos = [False] * int(clip.duration / args.gap_time)

    last_gap_time = 4
    while args.gap_time >= 1.0 / clip.fps + 0.001:  # 加0.001是为了防止精度误差
        args.gap_time = clip.duration / 2000
        args.gap_time = min(last_gap_time / 4.0, args.gap_time)  # 每次的精度至少是上一次的4倍
        print(f"开始检测，当前视频时长{clip.duration}，检测gap_time={args.gap_time}")
        clip = cut_video(clip, accept_infos, args)
        last_gap_time = args.gap_time

    clip.write_videofile(args.output_file, threads=args.threads)


def set_false_between(array, min_size):
    false_indices = [i for i, val in enumerate(array) if val is False]

    for i in range(len(false_indices) - 1):
        if false_indices[i + 1] - false_indices[i] <= min_size:
            start_index = false_indices[i]
            end_index = false_indices[i + 1]
            for j in range(start_index + 1, end_index):
                array[j] = False

    return array


def cut_video(clip, accept_infos, args):
    if args.gap_time < 1.0 / clip.fps:
        args.gap_time = 1.0 / clip.fps
        print(f"gap time 过低，重置为1/fps={args.gap_time}")
    get_face_analyser()

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        index = 0
        t = 0
        min_time = max(0, args.min_time)
        max_time = min(clip.duration, args.max_time)
        progress = tqdm(total=int((max_time - min_time) / args.gap_time))
        while t <= clip.duration and index < len(accept_infos):
            print(f"提交任务{index}")
            if args.max_time >= t >= args.min_time:
                frame = clip.get_frame(t)
                executor.submit(is_accept, frame, index, accept_infos, progress, args)
            if t >= args.max_time:
                break
            t += args.gap_time
            index = int(t * clip.fps)

    cut_times = get_index_range(accept_infos, args.accept_min_time * clip.fps)
    # 如果任何时间差小于accept_min_time的帧都为False，那中间的部分就不用检测了，直接设置为False
    set_false_between(accept_infos, args.accept_min_time * clip.fps + 1)
    for cut_time in cut_times:
        for i in range(len(cut_time)):
            cut_time[i] *= args.gap_time
    return do_cut_to_clip(clip, args, cut_times)


def do_cut_to_clip(clip, args, cut_times):
    sub_clips = []
    sum_time = 0
    with open(f"{args.input_file}.txt", 'w') as file:
        cut_info = {
            "cut_times": cut_times,
            "gap_time": args.gap_time
        }
        file.write(json.dumps(cut_info))
    print(cut_times)
    for cut_time in cut_times:
        s, e = cut_time
        print(f"实际使用的时间范围[{s}, {e}]")
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
