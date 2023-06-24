import os
from moviepy.video.io.VideoFileClip import VideoFileClip


def traverse_videos(folder_path):
    video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.rmvb']  # 可根据需要添加其他视频文件扩展名

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            if any(file_path.endswith(ext) for ext in video_extensions):
                basename = os.path.basename(file_path)  # 获取不带路径的文件名
                if basename.startswith("._"):
                    print(f"跳过：{file_path}")
                    continue
                name, extension = os.path.splitext(basename)  #
                clip = VideoFileClip(file_path,)
                clip.audio.write_audiofile(f"{folder_path}/{name}.mp3")


if __name__ == '__main__':
    traverse_videos("/Volumes/EXTERNAL/视频/袁腾飞/两宋风云")
