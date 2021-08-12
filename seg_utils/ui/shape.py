from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QPainterPath
from PyQt5.QtCore import QPointF, Qt, QRectF, QSize

from copy import deepcopy
from typing import Tuple, Union, List, Optional
import numpy as np
from seg_utils.config import VERTEX_SIZE, SCALING_INITIAL

from seg_utils.utils.qt import closestEuclideanDistance


class Shape(QGraphicsItem):
    def __init__(self,
                 image_size: QSize,
                 label: str = None,
                 points: List[QPointF] = [],
                 color: QColor = None,
                 shape_type: str = None,
                 flags=None,
                 group_id=None):
        super(Shape, self).__init__()
        self.image_size = image_size
        self.image_rect = QRectF(0, 0, self.image_size.width(), self.image_size.height())
        self.label = label
        self.shape_type = shape_type
        self.vertex_size = VERTEX_SIZE
        self.points = points
        self.flags = flags
        self.group_id = group_id
        self.line_color, self.brush_color = None, None
        self.initColor(color)
        self.selected_color = Qt.GlobalColor.white
        self.path = None
        self.vertices = None
        self._bounding_rect = None
        self._anchorPoint = None

        # distinction between highlighted (hovering over it) and selecting it (click)
        self.b_isHighlighted = False
        self.b_isClosedPath = False
        self.b_isSelected = False
        self.initShape()

    def __repr__(self):
        return f"Shape [{self.label.capitalize()}, {self.shape_type.capitalize()}]"

    def __eq__(self, other):
        if self.points == other.points and self.label == other.label:
            return True
        else:
            return False

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def from_dict(self, label_dict: dict, color: QColor):
        r"""Method to create a Shape from a dict, which is stored in the SQL database"""
        if 'label' in label_dict:
            self.label = label_dict['label']
        if 'points' in label_dict:
            self.points = [QPointF(_pt[0], _pt[1]) for _pt in label_dict['points']]
        if 'shape_type' in label_dict:
            self.shape_type = label_dict['shape_type']
        if 'flags' in label_dict:
            self.flags = label_dict['flags']
        if 'group_id' in label_dict:
            self.group_id = label_dict['group_id']

        self.initColor(color)
        self.initShape()
        return self

    def to_dict(self):
        r"""Method to store the current shape in the SQL Database"""
        pass

    def initShape(self):
        if self.shape_type not in ['polygon', 'rectangle', 'lines', 'circle', 'trace', None]:
            raise AttributeError("Unsupported Shape")
        # Add additional points
        if self.shape_type in ['rectangle', 'circle'] and len(self.points) == 2:
            self.getCorners()
        if self.shape_type in ['polygon', 'rectangle', 'lines', 'trace']:
            self.initPath()
            self.vertices = VertexCollection(self.points, self.line_color, self.brush_color, self.vertex_size)
            self._bounding_rect = self.path.boundingRect()

        elif self.shape_type == "circle":
            self.vertices = VertexCollection(self.points, self.line_color, self.brush_color, self.vertex_size)
            self._bounding_rect = QRectF(self.points[0], self.points[2])

    def initPath(self):
        self.path = QPainterPath()
        self.path.moveTo(self.points[0])
        for _pnt in self.points[1:]:
            self.path.lineTo(_pnt)
        if self.shape_type not in ['lines', 'trace']:
            # This is for drawing the initial traces and polygons such that they do not end and close immediately
            self.path.closeSubpath()

    def initColor(self, color: QColor):
        if color:
            self.line_color, self.brush_color = color, deepcopy(color)
            self.brush_color.setAlphaF(0.5)

    def updateColor(self, color: QColor):
        if color:
            self.line_color, self.brush_color = color, deepcopy(color)
            self.brush_color.setAlphaF(0.5)
            self.vertices.updateColor(self.line_color, self.brush_color)

    def getCorners(self):
        """This function generates the other bounding points of the shape"""
        self.points.insert(1, QPointF(self.points[1].x(), self.points[0].y()))
        self.points.append(QPointF(self.points[0].x(), self.points[2].y()))

    def resetAnchor(self):
        """Resets the anchor set """
        self._anchorPoint = None

    def updateShape(self, vNum: int, newPos: QPointF):
        if self.shape_type == 'polygon':
            if self.path.elementAt(vNum):
                self.path.setElementPositionAt(vNum, newPos.x(), newPos.y())
                self.points[vNum] = newPos
                self.vertices.vertices[vNum] = newPos
        elif self.shape_type in ['rectangle', 'circle']:
            if not self._anchorPoint:
                # this point is the anchor a.k.a the point diagonally from the selected one
                # however, as i am rebuilding the shape from there, i only need to select the anchor once and store it
                self._anchorPoint = self.points[vNum - 2]
            self.points = [self._anchorPoint, newPos]
            if self.shape_type in ['rectangle', 'circle'] and len(self.points) == 2:
                self.getCorners()
            if self.shape_type in ['polygon', 'rectangle', 'lines', 'trace']:
                self.initPath()
                # reset the selected vertex as the ordering within the bounding rectangle changes
                self.vertices.vertices = self.points
                self.vertices.updateSelAndHigh(np.asarray([newPos.x(), newPos.y()]))
                self._bounding_rect = self.path.boundingRect()

            elif self.shape_type == "circle":
                self.vertices.vertices = self.points
                self.vertices.updateSelAndHigh(np.asarray([newPos.x(), newPos.y()]))
                self._bounding_rect = QRectF(self.points[0], self.points[2])

    def paint(self, painter: QPainter) -> None:
        if len(self.points) > 0:
            if not self.b_isSelected:
                painter.setPen(QPen(self.line_color, 1))  # TODO: pen width depending on the image size
            else:
                painter.setPen(QPen(self.selected_color, 1))
            if self.b_isHighlighted or self.b_isSelected:
                painter.setBrush(QBrush(self.brush_color))
            else:
                painter.setBrush(QBrush())
            if self.shape_type in ['polygon', 'rectangle', 'lines', 'trace']:
                painter.drawPath(self.path)
                self.vertices.paint(painter)
            elif self.shape_type == "circle":
                painter.drawEllipse(QRectF(self.points[0], self.points[2]))
                if self.b_isSelected or self.b_isHighlighted or self.vertices.selectedVertex != -1:
                    self.vertices.paint(painter)

    def setScaling(self, zoom: int, max_size: int):
        r"""Sets the zoom coming from the imageviewer as the vertices can be displayed with different size.
        Currently, the max size is not used but is left in for future iterations"""
        if zoom <= 5:
            _scaling = SCALING_INITIAL/zoom
        else:
            _scaling = 1
        self.vertices._scaling = _scaling

    def contains(self, point: QPointF) -> bool:
        r"""Reimplementation as the initial method for a QGraphicsItem uses the shape,
        which results in the bounding rectangle"""

        if self.shape_type in ['rectangle', 'polygon']:
            return self.path.contains(point)

        elif self.shape_type in ['circle']:
            # elliptic formula is (x²/a² + y²/b² = 1) so if the point fulfills the equation respectively
            # is smaller than 1, the points is inside
            rect = self.boundingRect()
            centerpoint = rect.center()
            a = rect.width()/2
            b = rect.height()/2
            value = (point.x()-centerpoint.x()) ** 2 / a ** 2 + (point.y() - centerpoint.y()) ** 2 / b ** 2
            if value <= 1:
                return True
            else:
                return False

    def move(self, displacement: QPointF) -> None:
        r"""Moves the shape by the given displacement"""
        self.points = self.checkBoundaries(displacement)
        self.vertices.vertices = self.points
        if self.shape_type in ['polygon', 'rectangle', 'lines', 'trace']:
            self.initPath()
            self._bounding_rect = self.path.boundingRect()

        elif self.shape_type == "circle":
            self._bounding_rect = QRectF(self.points[0], self.points[2])

    def checkBoundaries(self, displacement: QPointF) -> List[QPointF]:
        """This founction checks whether the bounding rect of the current shape exceeds the image if the
        displacement is applied. If so, no displacement is applied"""
        new_br = deepcopy(self.boundingRect())
        new_br.setTopLeft(new_br.topLeft()-displacement)
        new_br.setTopRight(new_br.topRight()-displacement)
        new_br.setBottomLeft(new_br.bottomLeft() - displacement)
        new_br.setBottomRight(new_br.bottomRight() - displacement)
        if self.image_rect.contains(new_br):
            return [pt-displacement for pt in self.points]
        else:
            return self.points



    @staticmethod
    def toQPointFList(point_list: List[List[float]]) -> List[QPointF]:
        return [QPointF(*_pt) for _pt in point_list]

    @staticmethod
    def QPointFToList(point_list: List[QPointF]) -> List[List[float]]:
        return [[pt.x(), pt.y()] for pt in point_list]

    @staticmethod
    def QRectFToPoints(rectangle: QRectF) -> List[QPointF]:
        r"""This function returns the bounding points of a QRectF in clockwise order starting with the top left"""
        return [rectangle.topLeft(), rectangle.topRight(), rectangle.bottomRight(), rectangle.bottomLeft()]


class VertexCollection(object):
    def __init__(self, points: List[QPointF], line_color: QColor, brush_color: QColor, vertex_size):
        self.vertices = points
        self.line_color = line_color
        self.brush_color = brush_color
        self.highlight_color = Qt.GlobalColor.white
        self.vertex_size = vertex_size
        self._highlight_size = 1
        self.highlightedVertex = -1
        self.selectedVertex = -1
        self._scaling = SCALING_INITIAL

    def paint(self, painter: QPainter):
        for _idx, _vertex in enumerate(self.vertices):
            qtpoint = _vertex
            painter.setPen(QPen(self.line_color, 0.5))  # TODO: width dependent on the size of the image or something
            painter.setBrush(QBrush(self.brush_color))

            if _idx == self.selectedVertex:
                painter.setBrush(QBrush(self.highlight_color))
                painter.setPen(QPen(self.highlight_color, 0.5))
                size = (self.vertex_size * self._scaling) / 2

            elif _idx == self.highlightedVertex:
                painter.setBrush(QBrush(self.highlight_color))
                size = (self.vertex_size * self._scaling) / 2
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
        if closestVertex in [self.highlightedVertex, self.selectedVertex]:
            size = (self.vertex_size * self._scaling) / 2
        else:
            size = self.vertex_size / 2
        vertexRect = QRectF(vertexCenter - QPointF(size, size),
                            vertexCenter + QPointF(size, size))

        if vertexRect.contains(point):
            return True, closestVertex
        else:
            return False, -1

    def updateColor(self, line_color: QColor, brush_color: QColor):
        if line_color and brush_color:
            self.line_color = line_color
            self.brush_color = brush_color

    def updateSelAndHigh(self, newPos: np.ndarray):
        idx = self.closestVertex(newPos)
        self.selectedVertex = self.highlightedVertex = idx

    @staticmethod
    def ListQPointF_to_Numpy(point_list: List[QPointF]):
        return np.asarray([[_pt.x(), _pt.y()] for _pt in point_list])

