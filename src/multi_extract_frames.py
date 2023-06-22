import concurrent.futures

from moviepy.video.io.VideoFileClip import VideoFileClip


def do_extract_frames(start_index, size, file, callback):
    clip = VideoFileClip(file)
    clip.set_duration

def multi_extract_frames(file, executor, size, callback):
    for i in range(size):
        clip = VideoFileClip(file)
        total_frames = int(clip.fps * clip.duration)
        per_thread_frames = total_frames / size
        executor.submit(do_extract_frames, args=(per_thread_frames * i, per_thread_frames, file, callback))

