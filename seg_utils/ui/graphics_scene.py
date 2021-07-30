from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsItem
from PyQt5.QtGui import QPainterPath
from PyQt5.QtCore import Qt, pyqtSignal

from seg_utils.ui.shape import Shape


class imageViewerScene(QGraphicsScene):
    shapeSelected = pyqtSignal(Shape)
    shapeHovered = pyqtSignal(Shape)
    vertexHovered = pyqtSignal()  # TODO: implement the highlighting of the vertices

    def __init__(self, *args):
        super(imageViewerScene, self).__init__(*args)
        self._initialized = False

    def setInitialized(self, bool_: bool):
        self._initialized = bool_

    def mousePressEvent(self, event) -> None:
        # TODO: There has to be a nicer method
        pos = event.scenePos()
        for _item in self.items():
            if not isinstance(_item, QGraphicsPixmapItem):
                if _item.contains(event.scenePos()):
                    _item.isHighlighted = True
                    self.shapeSelected.emit(_item)
                else:
                    _item.isHighlighted = False

    def selectionChanged(self) -> None:
        four = 4

    def mouseMoveEvent(self, event) -> None:
        if self._initialized:
            for _item in self.items():
                if not isinstance(_item, QGraphicsPixmapItem):
                    if _item.contains(event.scenePos()):
                        _item.isHighlighted = True
                        self.shapeHovered.emit(_item)
                    else:
                        _item.isHighlighted = False

            #print(self.items()[0].isHighlighted, self.items()[1].isHighlighted, self.items()[2].isHighlighted)
        else:
            pass