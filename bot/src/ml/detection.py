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


def make_predict(bytes: BytesIO) -> str | tuple[tuple[Image, list[Image]], str]:
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

    if len(boxes) == 0:
        return "Нет дефектов"

    result_image, defect_images = generate_plots(image, cls, boxes, confs, errors)

    errors_counters = dict(Counter(cls))
    errors_counters = [f"{errors[key]["name"]} ({value})" for key, value in errors_counters.items()]
    text = "Обнаружены следующие ошибки: " + ", ".join(errors_counters)

    return (result_image, defect_images), text
