import concurrent.futures
import json
import os
import threading

from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip
from tqdm import tqdm

from src.analyser import get_face_many, get_face_analyser


def get_index_range(arr, accept_min_size):
    ranges = []
    start = None

    for i, value in enumerate(arr):
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


def is_accept(clip, t, index, accept_infos, progress, args):
    many_faces = get_face_many(clip.get_frame(t))
    male_faces = [face for face in many_faces if face['gender'] == 1]
    female_faces = [face for face in many_faces if face['gender'] == 0]
    accept = args.female_min <= len(female_faces) <= args.female_max and args.male_min <= len(
        male_faces) <= args.male_max
    accept_infos[index] = accept
    progress.update(1)


def copy_and_read_video(args, clips):
    source_file_name = None
    with open(args.input_file, 'rb') as file:
        data = file.read()
        print(f"拷贝数据，读取成功，长度：{len(data)}")
        source_file_name = file.name
    chunk_size = 4096
    num_chunks = len(data) // chunk_size

    for i in range(num_chunks):
        chunk_data = data[i * chunk_size: (i + 1) * chunk_size]
        new_file_name = f'cache/{source_file_name}_{i}'
        with open(new_file_name, 'wb') as new_file:
            new_file.write(chunk_data)
            new_file.flush()
            clips[i+1] = VideoFileClip(new_file_name)
            print(f"复制并加载第{i+1}个文件成功")

def cut_video(args):
    clips = [None] * (args.copies + 1)
    copy_and_read_video(args, clips);
    # threading.Thread(target=copy_and_read_video, args=(args, clips))
    clips[0] = VideoFileClip(args.input_file)
    fps = clips[0].fps
    if args.gap_time < 1.0 / fps:
        args.gap_time = 1.0 / fps
        print(f"gap time 过低，重置为1/fps={args.gap_time}")
    accept_infos = [False] * int(clips[0].duration / args.gap_time)
    get_face_analyser()

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        index = 0
        t = 0
        min_time = max(0, args.min_time)
        max_time = min(clips[0].duration, args.max_time)
        progress = tqdm(total=int((max_time - min_time) / args.gap_time))
        clip_index = 0
        while t <= clips[0].duration and index < len(accept_infos):
            if args.max_time >= t >= args.min_time:
                if clip_index >= len(clips) or (not clips[clip_index]):
                    clip_index = 0
                print(f"提交第{index}帧处理任务，clip_index={clip_index}")
                executor.submit(is_accept, clips[clip_index], t, index, accept_infos, progress, args)
                clip_index += 1
            if t >= args.max_time:
                break
            t += args.gap_time
            index += 1

    cut_times = get_index_range(accept_infos, args.accept_min_time * 1.0 / args.gap_time)
    for cut_time in cut_times:
        for i in range(len(cut_time)):
            cut_time[i] *= args.gap_time

    with open(f"{args.input_file}.txt", 'w') as file:
        cut_info = {
            "cut_times": cut_times,
            "gap_time": args.gap_time
        }
        file.write(json.dumps(cut_info))

    do_cut_video(args, cut_times)


def do_cut_video(args, cut_times):
    sub_clips = []
    tmp_clip = VideoFileClip(args.input_file)
    sum_time = 0
    for cut_time in cut_times:
        s, e = cut_time
        print(f"实际使用的时间范围[{s}, {e}]")
        sum_time += e - s
        try:
            sc = tmp_clip.subclip(s, e)
            sc = sc.set_audio(tmp_clip.audio.subclip(s, e))
            sub_clips.append(sc)
        except:
            print(f"提取片段时出现异常，片段:[{s}, {e}],")
            continue

    print(f"原时间:{tmp_clip.duration}，剪辑后的时长:{sum_time}")
    final_clip = concatenate_videoclips(sub_clips)
    final_clip.write_videofile(args.output_file, threads=args.threads)
