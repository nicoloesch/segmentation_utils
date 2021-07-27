import sys
from typing import List

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QFrame, QGraphicsPixmapItem, QMenu, QGraphicsPolygonItem
from PyQt5.QtGui import QPixmap, QKeySequence, QPolygonF, QBrush, QPen, QColor
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QPointF, QSize, QPoint

import imgviz

from seg_utils.src.context_menu import ContextMenu
from seg_utils.utils.qt import colormapRGB


class ImageViewer(QGraphicsView):
    #imageDragged = pyqtSignal(QPoint)

    def __init__(self, *args):
        super(QGraphicsView, self).__init__(*args)
        self._scene = QGraphicsScene(self)
        self._zoom = 0
        self._empty = True
        self.enableZoomPan = False
        self.setScene(self._scene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.image_size = QSize(0,0)

        # Painting specific
        self._num_colors = 25 # number of colors
        self._alpha = 0.5 # alpha channel responsible for opacity
        self.colors, drawNewColor = self.initColors()

        red = QColor(Qt.red)
        red.setAlphaF(0.7)

        # Painting stuff
        self.brush = QBrush(red)
        self.pen = QPen(Qt.white)
        self.pen.setWidth(1)


    def initColors(self):
        col = colormapRGB(n=self._num_colors, alpha=self._alpha)# have a buffer for new classes
        return col[:-1], col[-1]

    def fitInView(self, rect: QRectF, mode: Qt.AspectRatioMode = Qt.IgnoreAspectRatio) -> None:
        """This function displays the scene in the entirety of the Widget"""
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

    def setImage(self, pixmap: QPixmap, label_list: List[dict]):
        """This function sets the image and updates the pixmap of the QGraphicsView"""
        # clear the scene and remove everything previously created as it is stored in the SQL database anyways

        self._scene.clear()

        # plot the image
        if pixmap and not pixmap.isNull():
            self._empty = False
            self._scene.addPixmap(pixmap)
            self.image_size = pixmap.size()
        else:
            self._empty = True
            self._scene.addPixmap(QPixmap())

        # plot the labels
        self.drawLabels(label_list)

        self._zoom = 0
        self.setDragMode(QGraphicsView.NoDrag)  # disable initial dragging of the image
        self.fitInView(QRectF(pixmap.rect()))

    def drawLabels(self, label_list: List[dict]):
        """This function draws the labels"""
        for _label in label_list:
            points = _label["points"]
            if _label['shape_type'] == 'trace':
                if not isinstance(points[0], QPointF):
                    points = [QPointF(*_point) for _point in points]
                polygon = QPolygonF(points)
                self._scene.addPolygon(polygon, self.pen, self.brush)

            # draw vertices
            for _point in points:
                self._scene.addRect(self.QRectF_from_QPointF(_point), self.pen)

    def wheelEvent(self, event):
        """Responsible for Zoom. Redefines base function"""
        if not self._empty:
            if self.enableZoomPan:
                if event.angleDelta().y() > 0:
                    factor = 1.25
                    self._zoom += 1
                else:
                    factor = 0.8
                    self._zoom -= 1
                if self._zoom > 0:
                    self.scale(factor, factor)
                elif self._zoom == 0:
                    self.fitInView(QRectF(0.0, 0.0, self.image_size.width(), self.image_size.height()))
                else:
                    self._zoom = 0

    def keyPressEvent(self, event) -> None:
        if not self._empty:
            if event.key() == QKeySequence(Qt.Key_Control):
                self.enableZoomPan = True
                self.setDragMode(QGraphicsView.ScrollHandDrag)

    def keyReleaseEvent(self, event) -> None:
        if not self._empty:
            if event.key() == QKeySequence(Qt.Key_Control):
                self.enableZoomPan = False
                self.setDragMode(QGraphicsView.NoDrag)

    def contextMenuEvent(self, event) -> None:
        pass
        #contextMenu = QMenu(self)
        #action = contextMenu.exec_(self.mapToGlobal())

    @staticmethod
    def QRectF_from_QPointF(point: QPointF):
        #todo: replace with scaling factor depending on image size
        scale = 4
        return QRectF(point.x()-(scale/2), point.y()-(scale/2), scale, scale)

    """
    def mousePressEvent(self, event):
        if self._image.isUnderMouse():
            self.imageDragged.emit(self.mapToScene(event.pos()).toPoint())
        super(ImageViewer, self).mousePressEvent(event)
    """



