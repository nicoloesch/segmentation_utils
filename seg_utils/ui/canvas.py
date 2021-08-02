from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets


from typing import List

from seg_utils.ui.shape import Shape


class Canvas(QtWidgets.QWidget):
    r"""Base drawing widget as it should be instantiated and then connected to a scene
     https://forum.qt.io/topic/93327/how-can-i-use-qpainter-to-paint-on-qgraphicsview/3
     """
    # Place signals here
    requestFitInView = QtCore.pyqtSignal(QtCore.QRectF)

    def __init__(self, *args, **kwargs):
        super(Canvas, self).__init__(*args, **kwargs)
        self.colorMap, self.drawNewColor = None, None
        self.labels = []
        self.pixmap = QtGui.QPixmap()

    def setPixmap(self, pixmap: QtGui.QPixmap):
        r"""Sets the pixmap and resizes the Widget to the size of the pixmaps as this is just connected
        to the Scene and the image_viewer will display the scene respectively a view into the scene"""
        self.pixmap = pixmap
        self.resize(self.pixmap.size())
        self.requestFitInView.emit(QtCore.QRectF(self.pixmap.rect()))

    def setLabels(self, labels: List[Shape]):
        self.labels = labels
        self.update()

    def setScale(self, scale):
        self._scale = scale

    def setColors(self, colors: List[QtGui.QColor]):
        self.colorMap, self.drawNewColor = colors[:-1], colors[-1]

    """
    def wheelEvent(self, event):
        "Responsible for Zoom.Redefines base function"
        #if not self._empty:
            #if self.enableZoomPan:
        if event.angleDelta().y() > 0:
            factor = 1.25
            self._zoom += 1
        else:
            factor = 0.8
            self._zoom -= 1
        if self._zoom > 0:
            self._scale = factor
        elif self._zoom == 0:
            self.fitInView(QRectF(0.0, 0.0, self.image_size.width(), self.image_size.height()))
        else:
            self._zoom = 0
        self.update()
    """

    def paintEvent(self, event) -> None:
        if not self.pixmap:
            return super(Canvas, self).paintEvent(event)
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.setRenderHint(QtGui.QPainter.HighQualityAntialiasing)
        p.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        p.drawPixmap(0, 0, self.pixmap)
        if self.labels:
            for _label in self.labels:
                _label.paint(p)

        p.end()
        #self.requestFitInView.emit(QtCore.QRectF(self.pixmap.rect()))

