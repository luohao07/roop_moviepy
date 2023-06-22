import argparse

from src.auto_cut import cut_video

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video processing using MoviePy')
    parser.add_argument('-i', '--input_file', type=str, help='Input video file')
    parser.add_argument('-o', '--output_file', type=str, help='Output video file')
    parser.add_argument('-tn', '--threads', type=int, help='threads', default=16)
    parser.add_argument('-gt', '--gap_time', type=float, help='gap time pre check', default=0.1)
    parser.add_argument('-a', '--female_min', type=int, help='female_min', default=1)
    parser.add_argument('-b', '--female_max', type=int, help='female_max', default=10)
    parser.add_argument('-c', '--male_min', type=int, help='male_min', default=0)
    parser.add_argument('-d', '--male_max', type=int, help='male_max', default=10)
    args = parser.parse_args()
    cut_video(args)