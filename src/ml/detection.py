import os
from io import BytesIO
from PIL import Image
from ultralytics import YOLO
import numpy as np
from collections import Counter

from .utils import generate_plots
from .models_parsing import get_info_from_yolo_result
from .ensemble import get_ensemble_boxes
from .errors_mapping import errors


def make_predict(bytes: BytesIO):
    image = Image.open(bytes)

    boxes_list = []
    scores_list = []
    labels_list = []

    # Получение результатов с моделек
    # YOLO
    model = YOLO("src/ml/models/best.pt")

    result = model([image], iou=0.25, conf=0.15)[0]
    result = get_info_from_yolo_result(result)

    boxes_list.append(result[0])
    scores_list.append(result[1])
    labels_list.append(result[2])

    # Получаем ансамбль
    results = get_ensemble_boxes(boxes_list, labels_list, scores_list)

    boxes = np.array(results[0])[:, [2, 3, 0, 1]]
    cls = np.array(result[1], dtype="int")
    confs = np.array(result[2])

    if not boxes:
        return "Нет дефектов"

    result_image, defect_images = generate_plots(image, cls, boxes, confs, errors)

    result_image_file_buffer = BytesIO()
    result_image.save(result_image_file_buffer, format="jpeg")
    print(result_image_file_buffer)

    errors = dict(Counter(cls))
    errors = [f"{key} ({value})" for key, value in errors.items()]
    text = "Обнаружены следующие ошибки: " + ", ".join(errors)

    return result_image_file_buffer, text
