import ensemble_boxes


def get_ensemble_boxes(boxes_list, labels_list, scores_list, weights=None, iou_thr=0.5, skip_box_thr=0.0001, sigma=0.1, function="nms"):
    if function == "nms":
        return ensemble_boxes.nms(boxes_list, scores_list, labels_list, weights=weights, iou_thr=iou_thr)
    if function == "soft_nms":
        return ensemble_boxes.soft_nms(boxes_list, scores_list, labels_list, iou_thr=iou_thr, sigma=sigma, thresh=skip_box_thr)
    if function == "non_maximum_weighted":
        return ensemble_boxes.non_maximum_weighted(boxes_list, scores_list, labels_list, weights=weights, iou_thr=iou_thr, skip_box_thr=skip_box_thr)
    if function == "weighted_boxes_fusion":
        return ensemble_boxes.weighted_boxes_fusion(boxes_list, scores_list, labels_list, weights=weights, iou_thr=iou_thr, skip_box_thr=skip_box_thr)