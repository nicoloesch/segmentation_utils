from typing import List
import cv2
import numpy as np


def create_binary_maks(label_list: List[dict], image_size: List[int]):
    r"""This function creates a binary mask array for each label present in the label_list.
    If the same label category is present, individual masks are created with instance segmentation in mind
    rather than semantic segmentation.
    """
    binary_mask = []
    for _label in label_list:
        _bm = np.zeros(image_size, int)
        if _label['shape_type'] == 'trace':
            poly_points = np.asarray(_label['points'], int)
            # for some reason, indexing with another numpy array does not work
            # but just with a list. One could do the stuff listed here
            # https://stackoverflow.com/questions/47370718/indexing-numpy-array-by-a-numpy-array-of-coordinates
            # or use mine, which transposes the individual Nx2 points to 2xN which can index the array

            _bm[poly_points.transpose().tolist()] = 1
            binary_mask.append(_bm)
    return binary_mask
