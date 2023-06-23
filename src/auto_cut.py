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
    accept_infos = [None] * int(clip.duration * clip.fps)

    for gap_time in args.gap_times:
        print(f"开始剪辑gap_time={gap_time}")
        args.gap_time = gap_time
        cut_video(clip, accept_infos, args)

    cut_frames = get_index_range(accept_infos, args.accept_min_time * clip.fps)
    for arr in cut_frames:
        for i in range(len(arr)):
            arr[i] = arr[i] * 1.0 / clip.fps

    cut_times = cut_frames

    try:
        new_clip = do_cut_to_clip(clip, args, cut_times)
        new_clip.write_videofile(args.output_file, threads=args.threads)
    except:
        print(f"合成失败！文件占用，现场已保存，可使用以下命令重试合成操作: ",
              f"python repay_cut.py --i {args.input_file} -o {args.output_file} -f {args.input_file}.txt")


def set_false_between(array, min_size):
    false_indices = [i for i, val in enumerate(array) if val is False]

    for i in range(len(false_indices) - 1):
        if false_indices[i + 1] - false_indices[i] - 1 <= min_size:
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

    fail_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        index = 0
        t = 0
        progress = tqdm(total=clip.duration / args.gap_time)
        while t <= clip.duration and index < len(accept_infos):
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
        print(f"任务提交结束：{t}, {index}, {len(accept_infos)}")

    # 如果任意两个时间差小于accept_min_time的帧都为False，那中间的部分就不用检测了，直接设置为False
    set_false_between(accept_infos, args.accept_min_time * clip.fps)


def do_cut_to_clip(clip, args, cut_times, save_log = True):
    sub_clips = []
    sum_time = 0
    if save_log:
        with open(f"{args.input_file}.txt", 'w') as file:
            cut_info = {
                "cut_times": cut_times
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
