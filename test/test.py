import time

from moviepy.video.io.VideoFileClip import VideoFileClip
from tqdm import tqdm

if __name__ == '__main__':
    start = time.perf_counter()
    clip = VideoFileClip("./asserts/CJOD-320_01.mp4")
    progress = tqdm(total=clip.fps*clip.duration)
    for frame in clip.iter_frames():
        progress.update(1)

