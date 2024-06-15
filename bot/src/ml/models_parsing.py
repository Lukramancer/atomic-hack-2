from ultralytics.engine import results


def get_info_from_yolo_result(result: results.Results):
    boxes = result.boxes
    boxes_coords = boxes.xywhn.numpy()
    labels = boxes.cls.numpy()
    scores = boxes.conf.numpy()

    return boxes_coords, labels, scores