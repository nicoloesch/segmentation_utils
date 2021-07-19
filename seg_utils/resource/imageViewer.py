import sys
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QFrame, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QPoint


class ImageViewer(QGraphicsView):
    imageDragged = pyqtSignal(QPoint)

    def __init__(self, *args):
        QGraphicsView.__init__(self, *args)
        self._scene = QGraphicsScene(self)
        self._zoom = 0
        self._image = QGraphicsPixmapItem()
        self._scene.addItem(self._image)
        self._empty = True
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)

    def fitInView(self, rect: QRectF, mode: Qt.AspectRatioMode = Qt.IgnoreAspectRatio) -> None:
        if not rect.isNull():
            self.setSceneRect(rect)
            if not self._empty:
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setImage(self, pixmap: QPixmap):
        """This function sets the image and updates the pixmap of the QGraphicsView"""
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._image.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._image.setPixmap(QPixmap())
        self.fitInView(QRectF(self._image.pixmap().rect()))

    def wheelEvent(self, event):
        if not self._empty:
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView(QRectF(self._image.pixmap().rect()))
            else:
                self._zoom = 0

    def mousePressEvent(self, event):
        if self._image.isUnderMouse():
            self.imageDragged.emit(self.mapToScene(event.pos()).toPoint())
        super(ImageViewer, self).mousePressEvent(event)



