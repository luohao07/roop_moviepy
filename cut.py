import argparse

from src.auto_cut import cut_video_wrap

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video processing using MoviePy')
    parser.add_argument('-i', '--input_file', type=str, help='Input video file')
    parser.add_argument('-o', '--output_file', type=str, help='Output video file')
    parser.add_argument('-tn', '--threads', type=int, help='threads', default=16)
    parser.add_argument('-gt', '--gap_times', nargs='+', type=float, help='gap time pre check', default=None)
    parser.add_argument('-a', '--female_min', type=int, help='female_min', default=1)
    parser.add_argument('-b', '--female_max', type=int, help='female_max', default=10)
    parser.add_argument('-c', '--male_min', type=int, help='male_min', default=0)
    parser.add_argument('-d', '--male_max', type=int, help='male_max', default=10)
    parser.add_argument('-amt', '--accept_min_time', type=float, help='accept_min_time', default=2)
    parser.add_argument('-maxt', '--max_time', type=float, help='max_time', default=None)
    parser.add_argument('-mint', '--min_time', type=float, help='min_time', default=None)
    parser.add_argument('-cp', '--copies', type=int, help='copies', default=1)
    args = parser.parse_args()
    cut_video_wrap(args)
