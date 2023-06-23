from moviepy.editor import VideoClip
from moviepy.video.io.VideoFileClip import VideoFileClip
if __name__ == '__main__':
    file_path = "../asserts/2.mov"  # 文件路径

    with open(file_path, "rb") as file:
        video_bytes = file.read()
    # 假设你已经有视频的字节数据，存储在变量 video_bytes 中

    # 创建一个 FFMPEG_VideoReader 对象，并从字节数据中加载视频
    video_reader = VideoFileClip(video_bytes)

    # 使用 VideoClip.from_video_reader 方法创建一个 VideoClip 对象
    video_clip = VideoClip.from_video_reader(video_reader)

    # 现在你可以使用 video_clip 进行各种操作，比如裁剪、添加特效等

    # 例如，将视频裁剪为前 10 秒
    video_clip = video_clip.subclip(0, 10)

    # 输出视频
    video_clip.write_videofile("output.mp4")

    # 记得最后要关闭 FFMPEG_VideoReader 对象
    video_reader.close()
    # 现在，文件的内容已经存储在变量 file_contents 中
