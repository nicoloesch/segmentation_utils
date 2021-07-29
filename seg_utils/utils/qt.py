import os.path as osp

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QListWidgetItem
from PyQt5.QtGui import QPixmap, QIcon, QColor
from PyQt5.QtGui import QPainter, QBrush, QPen, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QRect, QSize

import cv2
from typing import List, Tuple
import matplotlib
from matplotlib import cm
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


def colormapRGB(n: int, colormap: str = 'hsv') -> List[QColor]:
    # TODO: replace get_cmap by own function
    r"""Creates a colormap with n colors"""
    cmap = cm.get_cmap(colormap, n)
    return [QColor.fromRgbF(*cmap(idx)) for idx in range(n)]


def createListWidgetItemWithSquareIcon(text: str, color: QColor, size: int = 5) -> QListWidgetItem:
    pixmap = QPixmap(size, size)
    painter = QPainter(pixmap)
    painter.setPen(color)
    painter.setBrush(color)
    painter.drawRect(QRect(0, 0, size, size))
    icon = QIcon(pixmap)
    painter.end()
    return QListWidgetItem(icon, text)


def getIcon(icon):
    thisFile = osp.dirname(osp.abspath(__file__))
    icons_dir = osp.join(thisFile, "../icons")
    return QIcon(osp.join(":/", icons_dir, "%s.png" % icon))


def QSizeToList(size: QSize):
    return [size.width(), size.height()]
