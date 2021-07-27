import os.path as osp
from PyQt5.QtGui import QIcon, QColor, QRgba64
from PyQt5.QtCore import QSize
import cv2
from typing import List
import imgviz
import numpy as np

class Label(object):
    def __init__(
            self,
            label=None,
            shape_type=None,
            points=None,
            flags=None,
            group_id=None,
    ):
        self.label = label
        self.group_id = group_id
        self.points = points
        self.shape_type = shape_type
        self.flags = flags

    def __repr__(self):
        return f"Label Struct({self.label}, {self.shape_type})"

    def from_dict(self, item: dict):
        if 'label' in item:
            self.label = item['label']
        if 'shape_type' in item:
            self.shape_type = item['shape_type']
        if 'points' in item:
            self.points = item['points']
        if 'flags' in item:
            self.flags = item['flags']
        if 'group_id' in item:
            self.group_id = item['group_id']


def colormapRGB(n: int, alpha: float) -> List[float]:
    # TODO: replace label_colormap by own function
    assert 0.0 <= alpha <= 1.0
    col = imgviz.label_colormap(n_label=n)
    _alpha = np.full((n,1), alpha*256)
    col = np.concatenate((col, _alpha), axis=1).astype(int).tolist()

    return [QColor(*_col) for _col in col]






def getIcon(icon):
    thisFile = osp.dirname(osp.abspath(__file__))
    icons_dir = osp.join(thisFile, "../icons")
    return QIcon(osp.join(":/", icons_dir, "%s.png" % icon))


def QSizeToList(size: QSize):
    return [size.width(), size.height()]
