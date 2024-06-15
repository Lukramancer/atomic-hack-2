import os
from io import BytesIO
from PIL import Image
from ultralytics import YOLO
import numpy as np

from .utils import plot_images
from .models_parsing import get_info_from_yolo_result
from .ensemble import get_ensemble_boxes


def make_predict(bytes: BytesIO):
    image = Image.open(bytes)

    boxes_list = []
    scores_list = []
    labels_list = []

    # Получение результатов с моделек
    # YOLO
    print(os.getcwd())
    model = YOLO("src/ml/models/best.pt")

    result = model([image])[0]
    result = get_info_from_yolo_result(result)

    boxes_list.append(result[0])
    scores_list.append(result[1])
    labels_list.append(result[2])

    # Получаем ансамбль
    results = get_ensemble_boxes(boxes_list, labels_list, scores_list)

    images_batch = np.transpose(np.asarray([image]), [0, 3, 1, 2])
    print(results[0])

    boxes = np.array(results[0])[:, [2, 3, 0, 1]]
    print(boxes)

    return plot_images(images_batch, 1, cls=np.array([results[1]]), bboxes=np.array([boxes]),
                       confs=np.array([results[2]]), save=False)