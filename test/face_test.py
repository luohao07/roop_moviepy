import os

import cv2

from src.analyser import get_face_many, get_face_single


def get_face_info(path):
    try:
        face = get_face_single(cv2.imread(path))
        if face:
            return face.det_score
        return 0
    except Exception:
        return 0


if __name__ == '__main__':
    for root, dirs, files in os.walk('../asserts/'):
        for file in files:
            print(f"{file} \t{get_face_info(f'{root}/{file}')}")