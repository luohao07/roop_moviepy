import argparse

from src.core import main

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video processing using MoviePy')
    parser.add_argument('-i', '--input_file', type=str, help='Input video file')
    parser.add_argument('-o', '--output_file', type=str, help='Output video file')
    parser.add_argument('-f', '--source_imgs', nargs='+', type=str, help='Image file paths')
    parser.add_argument('-n', '--max_frames', nargs='+', type=str, help='max frames to reface')
    parser.add_argument('-tn', '--threads', type=int, help='threads', default=16)
    parser.add_argument('-l', '--log_level', type=str, help='log level', default="INFO")
    args = parser.parse_args()
    main(args)