import concurrent.futures

from moviepy.video.io.VideoFileClip import VideoFileClip


def do_extract_frames(start_index, size, file, callback):
    clip = VideoFileClip(file)
    start_time = start_index * (1.0 / clip.fps)
    for index in range(size):
        frame = clip.get_frame(start_time + index * (1.0 / clip.fps))
        callback(index, frame)


def multi_extract_frames(file, args, callback):
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.extract_threads) as executor:
        for i in range(args.extract_threads):
            print(f"提交第{i}次任务")
            clip = VideoFileClip(file)
            total_frames = int(clip.fps * clip.duration)
            per_thread_frames = total_frames / args.extract_threads
            executor.submit(do_extract_frames, per_thread_frames * i, per_thread_frames, file, callback)

