from PyQt5.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent
from PyQt5.QtCore import Qt, pyqtSignal, QPointF, QRectF

from seg_utils.utils.qt import isInCircle
from seg_utils.config import VERTEX_SIZE

from typing import Tuple
from numpy import argmax


class ImageViewerScene(QGraphicsScene):
    sig_ShapeHovered = pyqtSignal(int)
    sig_ShapeSelected = pyqtSignal(int, int, int)
    sig_VertexHovered = pyqtSignal()  # TODO: MAYBE implement the highlighting of the vertices

    sig_Drawing = pyqtSignal(list, str)
    sig_DrawingDone = pyqtSignal(list, str)

    CREATE, EDIT = 0, 1

    def __init__(self, *args):
        super(ImageViewerScene, self).__init__(*args)
        self.b_isInitialized = False
        self.mode = self.EDIT
        self.shape_type = None
        self.starting_point = QPointF()
        self._startButtonPressed = False
        self.poly_points = []  # list of points for the polygon drawing

    def isInDrawingMode(self) -> bool:
        """Returns true if currently in drawing mode"""
        return self.mode == self.CREATE

    def setShapeType(self, shape_type: str):
        self.shape_type = shape_type

    def setMode(self, mode: int):
        assert mode in [self.CREATE, self.EDIT]
        self.mode = mode

    def setClosedPath(self):
        self._startButtonPressed = False
        self.sig_DrawingDone.emit(self.poly_points, self.shape_type)
        self.poly_points = []
        self.starting_point = QPointF()

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        r"""Handle the event for pressing the mouse. Handling of shape selection and of drawing for various shapes
        """
        if self.b_isInitialized:
            if event.button() == Qt.MouseButton.LeftButton:
                if self.isInDrawingMode():
                    self._startButtonPressed = True
                    self.starting_point = event.scenePos()
                    if self.shape_type in ['polygon']:
                        if self.isOnBeginning(self.starting_point) and len(self.poly_points) > 1:
                            self.setClosedPath()
                        else:
                            self.poly_points.append(self.starting_point)
                            self.sig_Drawing.emit(self.poly_points, self.shape_type)
                else:
                    hShape, vShape, vNum = self.isMouseOnShape(event)
                    self.sig_ShapeSelected.emit(hShape, vShape, vNum)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        r"""Handle the event for moving the mouse. Currently only for selecting the shapes
        whilst hovering over them"""
        if self.b_isInitialized:
            if self.isInDrawingMode():
                if self.shape_type in ['polygon']:
                    intermediate_points = self.poly_points + [event.scenePos()]
                    self.sig_Drawing.emit(intermediate_points, self.shape_type)
                else:
                    if self._startButtonPressed:
                        if self.shape_type in ['trace']:
                            self.poly_points.append(event.scenePos())
                            self.sig_Drawing.emit(self.poly_points, self.shape_type)
                        elif self.shape_type in ['circle', 'rectangle']:
                            self.sig_Drawing.emit([self.starting_point, event.scenePos()], self.shape_type)
            else:
                hShape, vShape, vNum = self.isMouseOnShape(event)
                self.sig_ShapeHovered.emit(hShape)

    def mouseReleaseEvent(self, event) -> None:
        if self.b_isInitialized:
            if event.button() == Qt.MouseButton.LeftButton:
                if self.isInDrawingMode():
                    if self.shape_type in ['circle', 'rectangle']:
                        # this ends the drawing for the above shapes
                        self._startButtonPressed = False
                        self.sig_DrawingDone.emit([self.starting_point, event.scenePos()], self.shape_type)
                        self.starting_point = QPointF()
                    elif self.shape_type in ['trace']:
                        self.setClosedPath()

    def isMouseOnShape(self, event: QGraphicsSceneMouseEvent) -> Tuple[int, int, int]:
        r"""Check if event position is within the boundaries of a shape

            :param event: Mouse Event on scene
            :returns: hovered shape index, closest shape index, vertex index
        """
        selected_shape = -1
        isOnVertex = []
        closestVertex = []
        # only contains one item which is the proxy item aka the canvas
        for _item_idx, _item in enumerate(self.items()[0].widget().labels):
            # Check if it is in the shape
            if _item.contains(event.scenePos()):
                selected_shape = _item_idx
            _isOnVert, _cVert = _item.vertices.isOnVertex(event.scenePos())
            isOnVertex.append(_isOnVert)
            closestVertex.append(_cVert)
        # check if any of them are True, i.e. the vertex is highlighted
        if any(isOnVertex):
            return selected_shape, int(argmax(isOnVertex)), closestVertex[argmax(isOnVertex)]
        else:
            return selected_shape, -1, -1

    def isOnBeginning(self, point: QPointF) -> bool:
        """Check if a point is within the area around the starting point"""
        if self.poly_points:
            vertexCenter = self.poly_points[0]
            size = VERTEX_SIZE / 2
            vertexRect = QRectF(vertexCenter - QPointF(size, size),
                                vertexCenter + QPointF(size, size))

            if vertexRect.contains(point):
                return True
            else:
                return False
        else:
            return False
