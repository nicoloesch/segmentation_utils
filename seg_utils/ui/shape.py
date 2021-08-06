from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath
from PyQt5.QtCore import QPointF, Qt, QRectF, QRect, pyqtSignal

from copy import deepcopy
from typing import Tuple, Union, List
import numpy as np
from seg_utils.config import VERTEX_SIZE

from seg_utils.utils.qt import closestEuclideanDistance


class Shape(QGraphicsItem):
    def __init__(self,
                 label: str = None,
                 points: List[QPointF] = [],
                 color: QColor = None,
                 shape_type: str = None,
                 flags=None,
                 group_id=None):
        super(Shape, self).__init__()
        self.label = label
        self.shape_type = shape_type
        self.vertex_size = VERTEX_SIZE
        self.points = points
        self.flags = flags
        self.group_id = group_id
        self.line_color, self.brush_color = self.initColor(color)
        self.selected_color = Qt.GlobalColor.white
        self.path = None
        self.vertices = None
        self._bounding_rect = None

        # distinction between highlighted (hovering over it) and selecting it (click)
        self.b_isHighlighted = False
        self.b_isSelected = False
        self.initShape()

    def __repr__(self):
        return f"Shape [{self.label.capitalize()}, {self.shape_type.capitalize()}]"

    def __eq__(self, other):
        if self.points == other.points and self.label == other.label:
            return True
        else:
            return False

    def initShape(self):
        if self.shape_type == 'rectangle':
            if len(self.points) == 2:
                # this means it is a rectangle consisting only of upper left and lower right hand corner
                self.points.insert(1, QPointF(self.points[1].x(), self.points[0].y()))  # upper right corner
                self.points.append(QPointF(self.points[0].x(), self.points[2].y()))  # lower left corner
            self.updatePath()
            self.closePath()
            self.vertices = VertexCollection(self.points, self.line_color, self.brush_color, self.vertex_size)
            self._bounding_rect = self.path.boundingRect()

        elif self.shape_type in ['trace', 'polygon']:
            self.updatePath()
            self.vertices = VertexCollection(self.points, self.line_color, self.brush_color, self.vertex_size)
            self._bounding_rect = self.path.boundingRect()

        elif self.shape_type == "circle":
            self.vertices = VertexCollection(self.points, self.line_color, self.brush_color, self.vertex_size)
            self._bounding_rect = QRectF(self.points[0], self.points[1])

    def updatePath(self):
        self.path = QPainterPath()
        self.path.moveTo(self.points[0])
        for _pnt in self.points[1:]:
            self.path.lineTo(_pnt)

    def closePath(self):
        self.path.closeSubpath()

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def boundingRectNonF(self) -> QRect:
        return QRect(*self._bounding_rect.getRect())

    def from_dict(self, label_dict: dict, color: QColor):
        r"""Method to create a Shape from a dict, which is stored in the SQL database"""
        if 'label' in label_dict:
            self.label = label_dict['label']
        if 'points' in label_dict:
            # TODO: right now i assume List[List[float, float]]
            #   has to be adapted as soon as i settled on how to save the stuff in the SQL database
            self.points = [QPointF(_pt[0], _pt[1]) for _pt in label_dict['points']]
        if 'shape_type' in label_dict:
            self.shape_type = label_dict['shape_type']
        if 'flags' in label_dict:
            self.flags = label_dict['flags']
        if 'group_id' in label_dict:
            self.group_id = label_dict['group_id']

        self.line_color, self.brush_color = self.initColor(color)
        self.initShape()
        return self

    def to_dict(self):
        r"""Method to store the current shape in the SQL Database"""
        pass

    def paint(self, painter: QPainter): # option: 'QStyleOptionGraphicsItem', widget: typing.Optional[QWidget] = ...) -> None:
        if len(self.points) > 0:
            if not self.b_isSelected:
                painter.setPen(QPen(self.line_color, 1))  # TODO: pen width depending on the image size
            else:
                painter.setPen(QPen(self.selected_color, 1))
            if self.b_isHighlighted or self.b_isSelected:
                painter.setBrush(QBrush(self.brush_color))
            else:
                painter.setBrush(QBrush())
            if self.shape_type in ['trace', 'polygon', 'rectangle']:
                painter.drawPath(self.path)
                self.vertices.paint(painter)
            elif self.shape_type == "circle":
                painter.drawEllipse(QRectF(self.points[0], self.points[1]))
                # maybe paint the vertices? But the bounding rect should only be visible on select

    def contains(self, point: QPointF) -> bool:
        r"""Reimplementation as the initial method for a QGraphicsItem uses the shape,
        which results in the bounding rectangle"""

        if self.shape_type in ['trace', 'rectangle', 'polygon']:
            return self.path.contains(point)

        elif self.shape_type in ['circle']:
            # elliptic formula is (x²/a² + y²/b² = 1) so if the point fulfills the equation respectively
            # is smaller than 1, the points is inside

            a = (self.points[0].x() - self.points[1].x())/2.0
            b = (self.points[0].y() - self.points[1].y())/2.0
            diagonal_vector = (self.points[1] - self.points[0])/2.0
            centerpoint = self.points[0] + diagonal_vector
            # TODO: maybe i dont need the abs here as i restrict it to the boundaries of the image
            centerpoint = QPointF(abs(centerpoint.x()), abs(centerpoint.y()))
            value = (point.x()-centerpoint.x()) ** 2 / a ** 2 + (point.y() - centerpoint.y()) ** 2 / b ** 2
            if value <= 1:
                return True
            else:
                return False

    @staticmethod
    def toQPointFList(point_list: List[List[float]]) -> List[QPointF]:
        return [QPointF(*_pt) for _pt in point_list]

    @staticmethod
    def initColor(color: QColor):
        if color:
            line_color, brush_color = color, deepcopy(color)
            brush_color.setAlphaF(0.5)
            return line_color, brush_color
        else:
            return None, None


class VertexCollection(object):
    def __init__(self, points: List[QPointF], line_color: QColor, brush_color: QColor, vertex_size):
        self.vertices = points
        self.line_color = line_color
        self.brush_color = brush_color
        self.highlight_color = Qt.GlobalColor.white
        self.vertex_size = vertex_size
        self._highlight_size = 0.1
        self.b_isHighlighted = False
        self.selectedVertex = -1

    def paint(self, painter: QPainter):
        for _idx, _vertex in enumerate(self.vertices):
            qtpoint = _vertex
            painter.setPen(QPen(self.line_color, 0.5))  # TODO: width dependent on the size of the image or something
            painter.setBrush(QBrush(self.brush_color))

            if _idx == self.selectedVertex:
                # highlight only the selected vertex
                painter.setBrush(QBrush(self.highlight_color))
                # size = (self.vertex_size+self._highlight_size) / 2
                size = self.vertex_size / 2
            else:
                size = self.vertex_size / 2  # determines the diagonal of the rectangle
            painter.drawRect(QRectF(qtpoint - QPointF(size, size),
                                    qtpoint + QPointF(size, size)))

    def closestVertex(self, point: np.ndarray) -> int:
        """Calculate the euclidean distance between a point and all vertices and return the index of
        the closest node to the point"""
        return closestEuclideanDistance(point, self.ListQPointF_to_Numpy(self.vertices))

    def isOnVertex(self, point: QPointF) -> Tuple[bool, int]:
        """Check if a point is within the closest vertex rectangle"""
        closestVertex = self.closestVertex(np.asarray([point.x(), point.y()]))
        vertexCenter = self.vertices[closestVertex]
        size = self.vertex_size / 2
        vertexRect = QRectF(vertexCenter - QPointF(size, size),
                            vertexCenter + QPointF(size, size))

        if vertexRect.contains(point):
            return True, closestVertex
        else:
            return False, -1

    @staticmethod
    def ListQPointF_to_Numpy(point_list: List[QPointF]):
        return np.asarray([[_pt.x(), _pt.y()] for _pt in point_list])