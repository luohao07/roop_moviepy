import cv2

from src.analyser import get_face_many

if __name__ == '__main__':

    faces = get_face_many(cv2.imread("../asserts/hy.jpeg"))
    print(faces)