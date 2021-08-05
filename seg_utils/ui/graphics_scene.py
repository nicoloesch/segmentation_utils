from PyQt5.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent
from PyQt5.QtCore import Qt, pyqtSignal, QPointF

from seg_utils.ui.shape import Shape
from seg_utils.utils.qt import closestEuclideanDistance

from typing import Tuple, List
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
        self._leftMouseButtonPressed = False

    def isInDrawingMode(self) -> bool:
        """Returns true if currently in drawing mode"""
        return self.mode == self.CREATE

    def setShapeType(self, shape_type: str):
        self.shape_type = shape_type

    def setMode(self, mode: int):
        assert mode in [self.CREATE, self.EDIT]
        self.mode = mode

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        r"""Handle the event for pressing the mouse. Currently only for selecting the shapes"""
        if self.b_isInitialized:
            if event.button() == Qt.MouseButton.LeftButton:
                if self.isInDrawingMode():
                    self._leftMouseButtonPressed = True
                    self.starting_point = event.scenePos()
                else:
                    hShape, vShape, vNum = self.isMouseOnShape(event)
                    self.sig_ShapeSelected.emit(hShape, vShape, vNum)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        r"""Handle the event for moving the mouse. Currently only for selecting the shapes
        whilst hovering over them"""
        if self.b_isInitialized:
            if self.isInDrawingMode():
                if self._leftMouseButtonPressed:
                    self.sig_Drawing.emit([self.starting_point, event.scenePos()], self.shape_type)
            else:
                hShape, vShape, vNum = self.isMouseOnShape(event)
                self.sig_ShapeHovered.emit(hShape)

    def mouseReleaseEvent(self, event) -> None:
        if self.b_isInitialized:
            if event.button() == Qt.MouseButton.LeftButton:
                if self.isInDrawingMode():
                    self._leftMouseButtonPressed = False
                    self.sig_DrawingDone.emit([self.starting_point, event.scenePos()], self.shape_type)
                    self.starting_point = QPointF()

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


