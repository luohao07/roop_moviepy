import unittest
from argparse import Namespace


def proccess():
 print(args)


class TestMain(unittest.TestCase):

    def test_main(self):
        # 构造参数命名空间对象
        args = Namespace(log_level="DEBUG",input_file='../asserts/d3.mp4', output_file='../output/output_video.mp4', source_imgs=['../asserts/hy.jpeg'], threads=10)
        # 调用 main 函数
        # main(args)

        proccess()

        # 在这里添加您的测试断言
        # ...


if __name__ == '__main__':
    unittest.main()
