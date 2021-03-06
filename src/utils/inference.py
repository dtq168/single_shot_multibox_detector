import numpy as np
from .boxes import decode_boxes
from .boxes import filter_boxes
from .boxes import denormalize_boxes
# from .boxes import create_prior_boxes
# from .boxes import apply_non_max_suppression
from .tf_boxes import apply_non_max_suppression
from preprocessing import load_image
from preprocessing import substract_mean


def predict(model, image_array, prior_boxes, original_image_shape,
            num_classes=21, class_threshold=.1,
            iou_nms_threshold=.45, background_index=0,
            box_scale_factors=[.1, .1, .2, .2], input_size=(300, 300)):

    image_array = np.expand_dims(image_array, axis=0)
    predictions = model.predict(image_array)
    predictions = np.squeeze(predictions)
    decoded_predictions = decode_boxes(predictions, prior_boxes)
    selected_boxes = filter_boxes(decoded_predictions,
                                  num_classes, background_index,
                                  class_threshold)
    if selected_boxes is None:
        return None
    selected_boxes = denormalize_boxes(selected_boxes, original_image_shape)
    supressed_boxes = []
    for class_arg in range(1, num_classes):
        best_classes = np.argmax(selected_boxes[:, 4:], axis=1)
        class_mask = best_classes == class_arg
        class_boxes = selected_boxes[class_mask]
        if len(class_boxes) == 0:
            continue
        class_boxes = apply_non_max_suppression(class_boxes, iou_nms_threshold)
        supressed_boxes.append(class_boxes)
    supressed_boxes = np.concatenate(supressed_boxes, axis=0)
    return supressed_boxes


def detect(predictions, prior_boxes, confidence_threshold=.01,
           iou_nms_threshold=.45, box_scale_factors=[.1, .1, .2, .2]):

    predictions = np.squeeze(predictions)
    decoded_boxes = decode_boxes(predictions, prior_boxes)
    scores = np.max(decoded_boxes[:, 4:], axis=1).copy()
    num_classes = predictions.shape[1] - 4
    detected_boxes = []
    for class_arg in range(1, num_classes):
        best_classes = np.argmax(decoded_boxes[:, 4:], axis=1)
        class_mask = best_classes == class_arg
        class_scores = scores[class_mask]
        if len(class_scores) == 0:
            continue
        else:
            confidence_mask = scores > confidence_threshold
            mask = np.logical_and(class_mask, confidence_mask)
            selected_boxes = decoded_boxes[mask].copy()
            supressed_boxes = apply_non_max_suppression(selected_boxes,
                                                        iou_nms_threshold)
            detected_boxes.append(supressed_boxes)
    if len(detected_boxes) == 0:
        return None
    else:
        detected_boxes = np.concatenate(detected_boxes, axis=0)
        return detected_boxes


def _infer(image_array, model, original_image_shape, prior_boxes):
    box_data_size = model.output_shape[1]
    image_array = substract_mean(image_array)
    image_array = np.expand_dims(image_array, 0)
    predictions = model.predict(image_array)
    # prior_boxes = create_prior_boxes()
    detections = detect(predictions, prior_boxes)
    if detections is None:
        return np.zeros(shape=(1, box_data_size))
    detections = denormalize_boxes(detections, original_image_shape)
    return detections


def infer_from_path(image_path, model, prior_boxes):
    target_size = model.input_shape[1:3]
    image_array, original_image_shape = load_image(image_path, target_size)
    detections = _infer(image_array, model, original_image_shape, prior_boxes)
    return detections


def infer_from_array(image_array, model, original_image_shape, prior_boxes):
    detections = _infer(image_array, model, original_image_shape, prior_boxes)
    return detections
