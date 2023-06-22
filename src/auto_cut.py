import concurrent.futures
from moviepy.video.io.VideoFileClip import VideoFileClip
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
        print(f"{_range}，时长为{e-s+1}，需要时长为{accept_min_size}")
        if e - s + 1 >= accept_min_size:
            accept_range.append(_range)

    return accept_range


def is_accept(frame, index, accept_infos, args):
    many_faces = get_face_many(frame)
    male_faces = [face for face in many_faces if face['gender'] == 1]
    female_faces = [face for face in many_faces if face['gender'] == 0]
    accept = args.female_min <= len(female_faces) <= args.female_max and args.male_min <= len(male_faces) <= args.male_max
    accept_infos[index] = accept


def cut_video(args):
    clip = VideoFileClip(args.input_file)
    accept_infos = [None] * int(clip.duration / args.gap_time)
    get_face_analyser()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        index = 0
        t = 0
        while t <= clip.duration and index < len(accept_infos):
            frame = clip.get_frame(t)
            executor.submit(is_accept, frame, index, accept_infos, args)
            t += args.gap_time
            index += 1

    cut_times = get_index_range(accept_infos, args.accept_min_time * 1.0 / args.gap_time)
    print(cut_times)



