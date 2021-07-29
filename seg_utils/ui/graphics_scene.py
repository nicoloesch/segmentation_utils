from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsItem
from PyQt5.QtGui import QPainterPath
from PyQt5.QtCore import Qt, pyqtSignal


class imageViewerScene(QGraphicsScene):
    shapeSelected = pyqtSignal(QPainterPath)
    shapeHovered = pyqtSignal(QGraphicsItem)

    def __init__(self, *args):
        super(imageViewerScene, self).__init__(*args)
        self._initialized = False

    def setInitialized(self, bool_: bool):
        self._initialized = bool_

    def mousePressEvent(self, event) -> None:
        # TODO: There has to be a nicer method
        pos = event.scenePos()
        for _item in self.items():
            path = _item.shape()
            if path.contains(event.scenePos()):
                self.shapeSelected.emit(path)

    def selectionChanged(self) -> None:
        four = 4

    def mouseMoveEvent(self, event) -> None:
        if self._initialized:
            for _item in self.items():
                if _item.shape().contains(event.scenePos()) and not isinstance(_item, QGraphicsPixmapItem):
                    # This makes the code faster es I emit the signal earlier and don't have to go through everything
                    self.shapeHovered.emit(_item)
        else:
            pass