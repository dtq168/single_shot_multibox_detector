import cv2
import matplotlib.pyplot as plt
import numpy as np
from utils.boxes import denormalize_boxes


# with openCV
def draw_video_boxes(box_data, original_image_array,
                     arg_to_class, colors, font):
    if len(box_data) == 0:
        return
    box_data = denormalize_boxes(box_data, original_image_array.shape[:2])
    x_min = box_data[:, 0]
    y_min = box_data[:, 1]
    x_max = box_data[:, 2]
    y_max = box_data[:, 3]
    classes = box_data[:, 4:]
    num_boxes = len(box_data)
    for box_arg in range(num_boxes):
        x_min_box = int(x_min[box_arg])
        y_min_box = int(y_min[box_arg])
        x_max_box = int(x_max[box_arg])
        y_max_box = int(y_max[box_arg])
        box_class_scores = classes[box_arg]
        label_arg = np.argmax(box_class_scores)
        score = box_class_scores[label_arg]
        class_name = arg_to_class[label_arg]
        color = colors[label_arg]
        display_text = '{:0.2f}, {}'.format(score, class_name)
        cv2.rectangle(original_image_array, (x_min_box, y_min_box),
                      (x_max_box, y_max_box), color, 2)
        cv2.putText(original_image_array, display_text,
                    (x_min_box, y_min_box - 30), font,
                    .7, color, 1, cv2.LINE_AA)


# with matplotlib
def draw_image_boxes(box_data, original_image_array,
                     arg_to_class=None, colors=None):
    if len(box_data) == 0:
        return None
    original_image_array = original_image_array.astype('uint8')
    figure, axis = plt.subplots(1)
    axis.imshow(original_image_array)
    x_min = box_data[:, 0]
    y_min = box_data[:, 1]
    x_max = box_data[:, 2]
    y_max = box_data[:, 3]
    if box_data.shape[1] > 4:
        classes = box_data[:, 4:]
        with_classes = True
        if colors is None:
            num_classes = classes.shape[1]
            colors = get_colors(num_classes)
    else:
        with_classes = False
    num_boxes = len(box_data)
    for box_arg in range(num_boxes):
        x_min_box = int(x_min[box_arg])
        y_min_box = int(y_min[box_arg])
        x_max_box = int(x_max[box_arg])
        y_max_box = int(y_max[box_arg])
        box_width = x_max_box - x_min_box
        box_height = y_max_box - y_min_box
        if with_classes:
            box_class_scores = classes[box_arg]
            label_arg = np.argmax(box_class_scores)
            score = box_class_scores[label_arg]
            class_name = arg_to_class[label_arg]
            color = colors[label_arg]
            display_text = '{:0.2f}, {}'.format(score, class_name)
            x_text = x_min_box
            y_text = y_min_box
            axis.text(x_text, y_text, display_text,
                      bbox={'facecolor': color, 'alpha': 0.5, 'pad': 10})
        else:
            color = 'r'

        rectangle = plt.Rectangle((x_min_box, y_min_box),
                                  box_width, box_height,
                                  linewidth=1, edgecolor=color,
                                  facecolor='none')
        axis.add_patch(rectangle)
    plt.show()


def plot_images(image_1, image_2, title_1='original image',
                title_2='transformed image'):
    plt.figure(1)
    plt.subplot(121)
    plt.title(title_1)
    plt.imshow(image_1.astype('uint8'))
    plt.subplot(122)
    plt.title(title_2)
    plt.imshow(image_2.astype('uint8'))
    plt.show()


def get_colors(num_colors=21):
    return plt.cm.hsv(np.linspace(0, 1, num_colors)).tolist()
