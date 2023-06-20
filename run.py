import argparse

from src.core import main

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video processing using MoviePy')
    parser.add_argument('-i', '--input_file', type=str, help='Input video file')
    parser.add_argument('-o', '--output_file', type=str, help='Output video file')
    parser.add_argument('-f', '--source_imgs', nargs='+', type=str, help='Image file paths')
    args = parser.parse_args()
    main(args)