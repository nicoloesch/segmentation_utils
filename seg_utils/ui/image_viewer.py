import sys
from typing import List
from copy import deepcopy

from PyQt5.QtWidgets import QGraphicsView, QFrame, QMenu, QGraphicsPolygonItem, QGraphicsItem
from PyQt5.QtGui import QPixmap, QKeySequence, QPolygonF, QBrush, QPen, QColor, QPainter, QPainterPath
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QPointF, QSize, QPoint

import imgviz

from seg_utils.ui.graphics_scene import imageViewerScene
from seg_utils.ui.shape import Shape


class ImageViewer(QGraphicsView):
    #imageDragged = pyqtSignal(QPoint)

    def __init__(self, *args):
        super(QGraphicsView, self).__init__(*args)
        self.colorMap, self.drawNewColor = None, None
        self.scene_ = imageViewerScene(self)
        self._zoom = 0
        self._empty = True
        self.enableZoomPan = False
        self.setScene(self.scene_)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.image_size = QSize(0,0)
        self.classes = {}
        self.labels = []

        # Painting specific
        self.pixmap = QPixmap()
        self._alpha = 0.3
        self.brush = QBrush()
        self.brush.setStyle(Qt.SolidPattern)

        self.pen = QPen()
        self.pen.setWidth(1)

        # Connect to events
        self.scene_.shapeSelected.connect(self.highlightLabel)
        self.scene_.shapeHovered.connect(self.highlightLabel)

    def initColors(self, color_map, classes: dict):
        r"""Initialize colors and also the respective classes dict necessary to know which class to draw.
        Gets called from the main class. drawNewColor is reserved if a new polygon etc. is drawn to have that
        as an exclusive color that cant be confused with others"""
        self.colorMap, self.drawNewColor = color_map[:-1], color_map[-1]
        self.classes = classes

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
        self.scene_.clear()

        # plot the image
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.pixmap = pixmap
            self.scene_.addPixmap(pixmap)
            self.image_size = pixmap.size()
        else:
            self._empty = True
            self.scene_.addPixmap(QPixmap())

        # plot the labels
        self.setLabels(label_list)

        self._zoom = 0
        self.setDragMode(QGraphicsView.NoDrag)  # disable initial dragging of the image
        self.fitInView(QRectF(pixmap.rect()))

    def setLabels(self, label_list: List[dict]):
        """This function draws the labels"""
        self.labels = []
        for _label in label_list:
            _shape = Shape.from_dict(Shape(), _label, self.colorMap[self.classes[_label['label']]])
            self.scene_.addItem(_shape)
            self.labels.append(_shape)

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
        four = 4
        pass
        #contextMenu = QMenu(self)
        #action = contextMenu.exec_(self.mapToGlobal())

    def polySelected(self, item) -> None:
        """Select Polygon from list and highlight it"""
        pass

    def highlightLabel(self, item: Shape):
        """Highlights a label"""
        self.repaint()

    """
    def paintEvent(self, event) -> None:
        p = QPainter()
        p.begin(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.HighQualityAntialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        p.scale(1.0, 1.0)
        p.drawPixmap(0, 0, self.pixmap)


        if self.labels:
            for _label in self.labels:
                _label.paint(p)

        p.end()
    """


    # If i am going to include a mousePressEvent, there needs to be a filter as graphics_scene also wants to have it
    """
    def mousePressEvent(self, event):
        if self._image.isUnderMouse():
            self.imageDragged.emit(self.mapToScene(event.pos()).toPoint())
        super(ImageViewer, self).mousePressEvent(event)
    """



