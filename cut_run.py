import argparse
import os.path

from moviepy.video.io.VideoFileClip import VideoFileClip

from src.auto_cut import cut_video_wrap
from src.core import main

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Video processing using MoviePy')
    parser.add_argument('-i', '--input_file', type=str, help='Input video file')
    parser.add_argument('-f', '--source_imgs', nargs='+', type=str, help='Image file paths')
    parser.add_argument('-tn', '--threads', type=int, help='threads', default=29)
    parser.add_argument('-l', '--log_level', type=str, help='log level', default="INFO")
    parser.add_argument('-g', '--gender', type=str, help='gender: male or female', default='female')
    parser.add_argument('-st', '--sleep_time', type=float, help='sleep time on wait', default=0.01)
    parser.add_argument('-mcf', '--max_cache_frames', type=float, help='sleep time on wait', default=500)

    parser.add_argument('-a', '--female_min', type=int, help='female_min', default=1)
    parser.add_argument('-b', '--female_max', type=int, help='female_max', default=10)
    parser.add_argument('-c', '--male_min', type=int, help='male_min', default=0)
    parser.add_argument('-d', '--male_max', type=int, help='male_max', default=10)
    parser.add_argument('-amt', '--accept_min_time', type=float, help='accept_min_time', default=2)
    parser.add_argument('-maxt', '--max_time', type=float, help='max_time', default=None)
    parser.add_argument('-mint', '--min_time', type=float, help='min_time', default=None)
    parser.add_argument('-cp', '--copies', type=int, help='copies', default=1)

    parser.add_argument('-it', '--item_time', type=int, help='split_time', default=1200)

    args = parser.parse_args()

    source_clip = VideoFileClip(args.input_file)
    start_time = 0
    end_time = args.item_time
    name, ext = os.path.splitext(args.input_file)
    face_file_identify = ""
    for face_file in args.source_imgs:
        face_file_name, face_file_ext = os.path.splitext(os.path.basename(face_file))
        face_file_identify += "_" + face_file_name
    index = 0
    while True:
        cut_file_name = f"{name}_{index}{ext}"
        out_file_name = f"{name}_{index}{face_file_identify}{ext}"
        print(
            f"开始处理第{index + 1}段，开始时间{start_time},结束时间{end_time},剪辑文件保存至{cut_file_name},输出文件保存至{out_file_name}")
        cut_args = argparse.Namespace(female_min=args.female_min, female_max=args.female_max, male_min=args.male_min,
                                      male_max=args.male_max, accept_min_time=args.accept_min_time, max_time=end_time,
                                      min_time=start_time, copies=args.copies, input_file=args.input_file,
                                      threads=args.threads, output_file=cut_file_name, gap_times=[0])
        cut_video_wrap(cut_args)
        print(f"剪辑已完成：{cut_file_name}")

        swap_args = argparse.Namespace(nput_file=cut_file_name, threads=args.threads, output_file=cut_file_name,
                                       source_imgs=args.source_imgs, log_level='INFO', gender='female', sleep_time=0.01,
                                       max_cache_frames=500)
        main(swap_args)
        print(f"换脸完成，输出路径：{out_file_name}")
        start_time += args.item_time
        end_time += args.item_time
