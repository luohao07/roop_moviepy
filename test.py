import argparse

from test.audio_test import cut_with_audio

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video processing using MoviePy')
    parser.add_argument('-i', '--input_file', type=str, help='Input video file')
    parser.add_argument('-o', '--output_file', type=str, help='Output video file')
    args = parser.parse_args()
    cut_with_audio(args)
