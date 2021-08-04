import sys
from typing import List
from copy import deepcopy

from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtCore import QSize, Qt, QRectF


from seg_utils.ui.graphics_scene import ImageViewerScene
from seg_utils.ui.shape import Shape
from seg_utils.ui.canvas import Canvas


class ImageViewer(QGraphicsView):

    def __init__(self, *args):
        super(ImageViewer, self).__init__(*args)
        self.canvas = Canvas()
        self.scene = ImageViewerScene(self)
        self.canvas.resize(QSize(0, 0))  # Makes it invisible
        self.proxy = self.scene.addWidget(self.canvas)
        self.setScene(self.scene)
        self.b_isEmpty = True

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        # Protected Item
        self._zoom = 0
        self._enableZoomPan = False

    def setInitialized(self):
        self.scene.b_isInitialized = True
        self.b_isEmpty = False

    def fitInView(self, rect: QRectF, mode: Qt.AspectRatioMode = Qt.AspectRatioMode.IgnoreAspectRatio) -> None:
        if not rect.isNull():
            self.setSceneRect(rect)
            if not self.b_isEmpty:
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def resizeEvent(self, event: QResizeEvent) -> None:
        bounds = self.scene.itemsBoundingRect()
        self.fitInView(bounds, Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event):
        """Responsible for Zoom.Redefines base function"""
        if not self.b_isEmpty:
            if self._enableZoomPan:
                if event.angleDelta().y() > 0:
                    # Forward Scroll
                    factor = 1.25
                    self._zoom += 1
                else:
                    # Backwards scroll
                    factor = 0.8
                    self._zoom -= 1

                if self._zoom > 0:
                    self.scale(factor, factor)
                elif self._zoom == 0:
                    self.fitInView(QRectF(self.canvas.rect()))
                else:
                    self._zoom = 0

    def keyPressEvent(self, event) -> None:
        if not self.b_isEmpty:
            if event.key() == Qt.Key.Key_Control:
                self._enableZoomPan = True
                self.setDragMode(QGraphicsView.ScrollHandDrag)

    def keyReleaseEvent(self, event) -> None:
        if not self.b_isEmpty:
            if event.key() == Qt.Key.Key_Control:
                self._enableZoomPan = False
                self.setDragMode(QGraphicsView.NoDrag)

    """
    def contextMenuEvent(self, event) -> None:
        four = 4
        pass
        #contextMenu = QMenu(self)
        #action = contextMenu.exec_(self.mapToGlobal())
    
    def mousePressEvent(self, event):
        if self._image.isUnderMouse():
            self.imageDragged.emit(self.mapToScene(event.pos()).toPoint())
        super(ImageViewer, self).mousePressEvent(event)
    """



