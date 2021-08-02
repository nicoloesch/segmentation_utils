from PyQt5.QtWidgets import QGraphicsItem, QWidget
from PyQt5.QtGui import QColor, QPainter, QPolygonF, QPen, QBrush
from PyQt5 import QtCore

from copy import deepcopy
import typing


class Shape(QGraphicsItem):
    def __init__(self,
                 label: str = None,
                 points=None,
                 line_color: QColor = None,
                 shape_type: str = None,
                 flags=None,
                 group_id=None,):
        super(Shape, self).__init__()
        self.label = label
        self.shape_type = shape_type
        self.points = points
        self.flags = flags
        self.group_id = group_id
        self.line_color, self.brush_color = None, None
        self.shape_ = None
        self.vertices = None
        self._bounding_rect = None

        self.isHighlighted = False

    def __repr__(self):
        return f"Shape [{self.label.capitalize()}, {self.shape_type.capitalize()}]"

    def initColor(self, color: QColor):
        self.line_color, self.brush_color = color, deepcopy(color)
        self.brush_color.setAlphaF(0.5)
        four = 4

    def initShape(self):
        if self.shape_type == 'trace':
            self.shape_ = QPolygonF([QtCore.QPointF(*_point) for _point in self.points])
            self._bounding_rect = self.shape_.boundingRect()
            self.vertices = VertexCollection(self.points, self.line_color, self.brush_color)

        elif self.shape_type == "circle":
            # also has a bounding rectangle which is used to draw it
            four = 4

        elif self.shape_type == "rectangle":
            four = 4

    def boundingRect(self) -> QtCore.QRectF:
        return self._bounding_rect

    def boundingRectNonF(self) -> QtCore.QRect:
        return QtCore.QRect(*self._bounding_rect.getRect())

    def from_dict(self, label_dict: dict, line_color: QColor):
        r"""Method to create a Shape from a dict, which is stored in the SQL database"""
        if 'label' in label_dict:
            self.label = label_dict['label']
        if 'points' in label_dict:
            self.points = label_dict['points']
        if 'shape_type' in label_dict:
            self.shape_type = label_dict['shape_type']
        if 'flags' in label_dict:
            self.flags = label_dict['flags']
        if 'group_id' in label_dict:
            self.group_id = label_dict['group_id']

        self.initColor(line_color)
        self.initShape()
        return self

    def to_dict(self):
        r"""Method to store the current shape in the SQL Database"""
        pass

    def paint(self, painter: QPainter): # option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
        if self.points:
            painter.setPen(QPen(self.line_color, 1)) # TODO: pen width depending on the image size
            if self.isHighlighted:
                painter.setBrush(QBrush(self.brush_color))
            else:
                painter.setBrush(QBrush())


            if self.shape_type == 'trace':
                painter.drawPolygon(self.shape_)
                self.vertices.paint(painter)
            elif self.shape_type == "circle":
                # also has a bounding rectangle which is used to draw it
                four = 4

            elif self.shape_type == "rectangle":
                four = 4

    def contains(self, point: typing.Union[QtCore.QPointF, QtCore.QPoint]) -> bool:
        r"""Reimplementation as the initial method for a QGraphicsItem uses the shape,
        which results in the bounding rectangle"""

        if type(self.shape_) == QPolygonF:
            if self.shape_.containsPoint(point, QtCore.Qt.FillRule.OddEvenFill):
                return True


class VertexCollection(object):
    def __init__(self, points, line_color, brush_color):
        self.vertices = [QtCore.QPointF(*_point) for _point in points]
        self.line_color = line_color
        self.brush_color = brush_color
        self.highlight_color = QtCore.Qt.white
        self.vertex_size = 3


    def paint(self, painter: QPainter):
        for _vertex in self.vertices:
            painter.setPen(QPen(self.line_color, 2)) # TODO: width dependent on the size of the image or something
            painter.setBrush(QBrush(self.brush_color))
            painter.drawRect(QtCore.QRectF(_vertex - QtCore.QPointF(self.vertex_size/2, self.vertex_size/2),
                                           _vertex + QtCore.QPointF(self.vertex_size/2, self.vertex_size/2))
                             )

