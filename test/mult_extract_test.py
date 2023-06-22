import concurrent.futures
from argparse import Namespace

from src.moviepy_utils import multi_extract_frames


def proccess_frame(index, frame):
    print(index)


if __name__ == '__main__':
    args = Namespace(extract_threads=10)
    multi_extract_frames("../asserts/d3.mp4", args, proccess_frame)
    print("finish")


