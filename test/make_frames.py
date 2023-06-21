from functools import partial

from moviepy.video.VideoClip import DataVideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip


def get_frame(clip, t):
    print(t)
    return clip.get_frame(t)


if __name__ == '__main__':
    clip = VideoFileClip("../asserts/d3.mp4")
    data = range(int(clip.fps * clip.duration))
    print(data)
    new_clip = DataVideoClip(data=data, data_to_frame=partial(get_frame, clip), fps=clip.fps)
    new_clip.write_videofile("output.mp4", threads=10)



