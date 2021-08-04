from PyQt5.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent
from PyQt5.QtCore import Qt, pyqtSignal

from seg_utils.ui.shape import Shape
from seg_utils.utils.qt import closestEuclideanDistance

from typing import Tuple
from numpy import argmax


class imageViewerScene(QGraphicsScene):
    sigShapeHovered = pyqtSignal(int)
    sigShapeSelected = pyqtSignal(int, int, int)
    sigVertexHovered = pyqtSignal()  # TODO: implement the highlighting of the vertices

    def __init__(self, *args):
        super(imageViewerScene, self).__init__(*args)
        self.isInitialized = False

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        r"""Handle the event for pressing the mouse. Currently only for selecting the shapes"""
        if self.isInitialized:
            hShape, vShape, vNum = self.isMouseOnShape(event)
            self.sigShapeSelected.emit(hShape, vShape, vNum)
        else:
            pass

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        r"""Handle the event for moving the mouse. Currently only for selecting the shapes
        whilst hovering over them"""
        if self.isInitialized:
            # get the highlighted shape, the vertex shape and the vertex number of the respective shape
            hShape, vShape, vNum = self.isMouseOnShape(event)
            self.sigShapeHovered.emit(hShape)
        else:
            pass

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


