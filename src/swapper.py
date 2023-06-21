import os
import threading

import cv2
import insightface as insightface

import src.globals
from src.analyser import get_face_many, get_face_single

FACE_SWAPPER = None
THREAD_LOCK = threading.Lock()


def read_all_faces(sources_imgs):
    faces = []
    for sources_img in sources_imgs:
        faces.append(get_face_single(cv2.imread(sources_img)))
    return faces


def process_frame(args, frame, progress=None):
    frame = process_faces(args.all_faces, frame)
    if progress:
        progress.update(1)
    return frame


def get_face_swapper():
    global FACE_SWAPPER
    with THREAD_LOCK:
        if FACE_SWAPPER is None:
            model_path = os.path.expanduser("~/.insightface/models/inswapper_128.onnx")
            print(model_path)
            FACE_SWAPPER = insightface.model_zoo.get_model(model_path, providers=src.globals.providers)
    return FACE_SWAPPER


def swap_face_in_frame(source_face, target_face, frame):
    if target_face:
        return get_face_swapper().get(frame, target_face, source_face, paste_back=True)
    return frame


def process_faces(source_faces, target_frame):
    many_faces = get_face_many(target_frame)
    many_faces = sorted(many_faces, key=lambda x: x['bbox'][0])
    many_faces = [face for face in many_faces if face['gender'] == 0]
    if not many_faces:
        return target_frame
    for index in range(len(source_faces)):
        if len(many_faces) < index:
            break
        target_frame = swap_face_in_frame(source_faces[index], many_faces[index], target_frame)
    return target_frame
