import sys
from typing import List
from copy import deepcopy

from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

import imgviz

from seg_utils.ui.graphics_scene import imageViewerScene
from seg_utils.ui.shape import Shape
from seg_utils.ui.canvas import Canvas


class ImageViewer(QtWidgets.QGraphicsView):
    #imageDragged = pyqtSignal(QPoint)

    def __init__(self, *args):
        super(ImageViewer, self).__init__(*args)
        self.canvas = Canvas()
        self.scene = imageViewerScene(self)
        self.canvas.resize(QtCore.QSize(0, 0))  # Makes it invisible
        self.proxy = self.scene.addWidget(self.canvas)
        self.setScene(self.scene)

        self._zoom = 0
        self._empty = True
        self._enableZoomPan = False
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)

        # signals
        self.canvas.requestFitInView.connect(self.fitInView)
        self.scene.shapeHovered.connect(self.canvas.isShapeHovered)
        self.scene.shapeSelected.connect(self.canvas.isShapeSelected)

    def setInitialized(self):
        self.scene.setInitialized()
        self._empty = False

    def four(self, event):
        four = 4

    def fitInView(self, rect: QtCore.QRectF, mode: QtCore.Qt.AspectRatioMode = QtCore.Qt.AspectRatioMode.IgnoreAspectRatio) -> None:
        if not rect.isNull():
            self.setSceneRect(rect)
            if not self._empty:
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        bounds = self.scene.itemsBoundingRect()
        self.fitInView(bounds, QtCore.Qt.AspectRatioMode.KeepAspectRatio)

    def wheelEvent(self, event):
        """Responsible for Zoom.Redefines base function"""
        if not self._empty:
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
                    self.fitInView(QtCore.QRectF(self.canvas.rect()))
                else:
                    self._zoom = 0

    def keyPressEvent(self, event) -> None:
        if not self._empty:
            if event.key() == QtCore.Qt.Key.Key_Control:
                self._enableZoomPan = True
                self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def keyReleaseEvent(self, event) -> None:
        if not self._empty:
            if event.key() == QtCore.Qt.Key.Key_Control:
                self._enableZoomPan = False
                self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

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



