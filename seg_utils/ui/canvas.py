from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets


from typing import List

from seg_utils.ui.shape import Shape


class Canvas(QtWidgets.QWidget):
    r"""Base drawing widget as it should be instantiated and then connected to a scene
     https://forum.qt.io/topic/93327/how-can-i-use-qpainter-to-paint-on-qgraphicsview/3
     """
    sigRequestFitInView = QtCore.pyqtSignal(QtCore.QRectF)
    sigRequestLabelListUpdate = QtCore.pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super(Canvas, self).__init__(*args, **kwargs)
        self.drawNewColor = None
        self.labels = [Shape]
        self.pixmap = QtGui.QPixmap()

    def setPixmap(self, pixmap: QtGui.QPixmap):
        r"""Sets the pixmap and resizes the Widget to the size of the pixmaps as this is just connected
        to the Scene and the image_viewer will display the scene respectively a view into the scene"""
        self.pixmap = pixmap
        self.resize(self.pixmap.size())
        self.sigRequestFitInView.emit(QtCore.QRectF(self.pixmap.rect()))

    def setLabels(self, labels: List[Shape]):
        """Set the labels which are drawn on the canvas"""
        self.labels = labels
        self.update()

    def setNewColor(self, color: QtGui.QColor):
        """Sets the color for drawing a new item"""
        self.drawNewColor = color

    @QtCore.pyqtSlot(int)
    def handleShapeHovered(self, _item_idx: int):
        for label in self.labels:
            label.isHighlighted = False
        if _item_idx > -1:
            self.labels[_item_idx].isHighlighted = True
        self.update()

    @QtCore.pyqtSlot(int)
    def handleShapeSelected(self, _item_idx: int):
        for label in self.labels:
            label.isSelected = False
        if _item_idx > -1:
            self.labels[_item_idx].isSelected = True
        self.sigRequestLabelListUpdate.emit(_item_idx)
        self.handleVertexHighlighted(_item_idx)
        self.update()

    @QtCore.pyqtSlot(int)
    def handleVertexHighlighted(self, _item_idx: int):
        r"""Only highlighted or not no matter if clicked or just hovered"""
        for _label in self.labels:
            _label.vertices.isHighlighted = False
        if _item_idx > -1:
            self.labels[_item_idx].vertices.isHighlighted = True

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

