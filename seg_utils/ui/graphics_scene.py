from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsItem
from PyQt5.QtGui import QPainterPath
from PyQt5.QtCore import Qt, pyqtSignal

from seg_utils.ui.shape import Shape


class imageViewerScene(QGraphicsScene):
    shapeSelected = pyqtSignal(Shape)
    shapeHovered = pyqtSignal()
    vertexHovered = pyqtSignal()  # TODO: implement the highlighting of the vertices

    def __init__(self, *args):
        super(imageViewerScene, self).__init__(*args)
        self._initialized = False

    def setInitialized(self):
        self._initialized = True

    def mousePressEvent(self, event) -> None:
        # TODO: There has to be a nicer method
        pos = event.scenePos()
        for _item in self.items():
            if not isinstance(_item, QGraphicsPixmapItem):
                if _item.contains(event.scenePos()):
                    _item.isHighlighted = True
                    #self.shapeSelected.emit(_item)
                else:
                    _item.isHighlighted = False

    def selectionChanged(self) -> None:
        four = 4

    def mouseMoveEvent(self, event) -> None:
        if self._initialized:
            for _item in self.items()[0].widget().labels:
                # Check if it is in the shape
                if _item.contains(event.scenePos()):
                    _item.isHighlighted = True
                else:
                    _item.isHighlighted = False

                # Check if it is on the path of rectangles depicting the border of the shape

            self.update()
        else:
            pass