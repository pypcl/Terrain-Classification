from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import cv2
import numpy as np
import math
from keras.utils import to_categorical


def crop_2d(image, top_left_corner, height, width):
    """
    Returns a crop of an image.

    Args:
        image: The original image to be cropped.
        top_left_corner: The coordinates of the top left corner of the image.
        height: The hight of the crop.
        width: The width of the crop.

    Returns:
        A cropped version of the original image.
    """

    x_start = top_left_corner[0]
    y_start = top_left_corner[1]
    x_end = x_start + width
    y_end = y_start + height

    return image[x_start:x_end, y_start:y_end, ...]


def prepare_images(image, size, ratio, n_slices):

    height = n_slices * ratio[1]
    width = n_slices * ratio[0]

    slice_height = int(size[1] / height)
    slice_width = int(size[0] / width)

    imgs = []

    for y in range(width):
        for x in range(height):
            tl_corner = (x * slice_height, y * slice_width)
            imgs.append(crop_2d(image, tl_corner, height=slice_height, width=slice_width))

    return np.stack(imgs)


def prepare_images_strided(image, window_size):
    w, h, d = image.shape
    window_w = window_size[0]
    window_h = window_size[1]
    shape = (h / window_h, w / window_w, window_h, window_w, d)
    strides = (
        image.strides[0] * window_h, image.strides[1] * window_w, image.strides[0], image.strides[1], image.strides[2])

    strided_image = np.lib.stride_tricks.as_strided(image,
                                                    shape=shape,
                                                    strides=strides)
    return strided_image.reshape((strided_image.shape[0] * strided_image.shape[1],) + strided_image.shape[-3:])


def retrieve_image(img, pos, slice_height, slice_width):
    """
    Retrieves window in which the position coordinates lie.

    :param img: A `ndarray` to be sliced.
    :param pos:
    :param slice_height:
    :param slice_width:
    :return: An `ndarray`.
    """
    if not 0 <= pos[0] < img.shape[0] or not 0 <= pos[1] < img.shape[1]:
        raise ValueError("Position coordinates out of range.")

    h = math.floor(pos[0] / slice_height)
    w = math.floor(pos[1] / slice_width)

    tl_corner = (int(h * slice_height), int(w * slice_width))

    return crop_2d(img, tl_corner, slice_height, slice_width)


def input_image_generator(image_list, label_list, image_size, ratio, n_slices):
    num_classes = len(list(set(label_list)))

    while True:

        for image_name, label in zip(image_list, label_list):
            img = cv2.imread(image_name)
            img_resize = cv2.resize(img, image_size)

            slices = prepare_images(img_resize, image_size, ratio, n_slices)

            labels = np.full((slices.shape[0]), label)
            one_hot_labels = to_categorical(labels, num_classes=num_classes)

            yield slices, one_hot_labels
