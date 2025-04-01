# Predict & blur

import cv2
from ultralytics import YOLO
import os, sys
import numpy as np
import glob
import main
import flet as ft


extensions = ("jpg", "png")


def yolo_detect(file_path):

    os.chdir(main.root_dir)

    files = glob.glob(f"{file_path}/*")

    # Load a model
    # model = YOLO("yolo11s.pt")  # pretrained YOLO11n model
    model = YOLO("src/yolo/best.pt")

    # Run batched inference on a list of images
    results = model(files, conf=0.25, stream=True)

    for result, imgName in zip(results, files):
        boxes = result.boxes  # Boxes object for bounding box outputs

        numpy_array = boxes.xyxy.numpy()

        img = cv2.imread(imgName)

        if numpy_array.any():
            for row in numpy_array:
                x1, y1, x2, y2 = [int(i) for i in row]

                roi = img[y1:y2, x1:x2]
                blur_image = cv2.GaussianBlur(roi, (41, 41), 0)
                img[y1:y2, x1:x2] = blur_image

        imgName = imgName.replace("\\", "/")
        tmp_path = f"src/assets/{imgName.split('/')[-2]}_done/"
        tmp_filename = imgName.split("/")[-1]

        # f_name = f"src/assets/{imgName.split('/')[-2]}_done/{os.path.basename(imgName)}"
        f_name = f"{tmp_path}{tmp_filename}"
        try:
            if not os.path.exists(tmp_path):
                os.makedirs(tmp_path)
        except OSError:
            print("Error: Creating directory. " + tmp_path)
            sys.exit(1)

        cv2.imwrite(f_name, img)  ### (path, img)


if __name__ == "__main__":
    yolo_detect()
