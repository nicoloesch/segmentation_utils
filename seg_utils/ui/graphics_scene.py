from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsItem
from PyQt5.QtGui import QPainterPath
from PyQt5.QtCore import Qt, pyqtSignal

from seg_utils.ui.shape import Shape


class imageViewerScene(QGraphicsScene):
    shapeHovered = pyqtSignal(int)
    shapeSelected = pyqtSignal(int)
    vertexHovered = pyqtSignal()  # TODO: implement the highlighting of the vertices

    def __init__(self, *args):
        super(imageViewerScene, self).__init__(*args)
        self._initialized = False

    def setInitialized(self):
        self._initialized = True

    def mousePressEvent(self, event) -> None:
        if self._initialized:
            selected_item = -1
            # only contains one item which is the proxy item aka the canvas
            for _item_idx, _item in enumerate(self.items()[0].widget().labels):
                # Check if it is in the shape
                if _item.contains(event.scenePos()):
                    selected_item = _item_idx

                # Check if it is on the path of rectangles depicting the border of the shape
            self.shapeSelected.emit(selected_item)
        else:
            pass

    def mouseMoveEvent(self, event) -> None:
        if self._initialized:
            highlighted_item = -1
            for _item_idx, _item in enumerate(self.items()[0].widget().labels):
                # Check if it is in the shape
                if _item.contains(event.scenePos()):
                    highlighted_item = _item_idx

                # Check if it is on the path of rectangles depicting the border of the shape
            self.shapeHovered.emit(highlighted_item)
        else:
            pass

    # TODO: hovering over vertex makes it appear bigger
