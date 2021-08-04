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
        self.resetHighlight()
        if _item_idx > -1:
            self.labels[_item_idx].isHighlighted = True
        self.update()

    def handleShapeSelected(self, item_idx: int, shape_idx: int, vertex_idx: int):
        self.resetSelection()
        if item_idx > -1:
            self.labels[item_idx].isSelected = True
        self.sigRequestLabelListUpdate.emit(item_idx)
        self.handleVertexHighlighted(shape_idx, vertex_idx)
        self.update()

    def handleVertexHighlighted(self, shape_idx: int, vertex_idx: int):
        r"""Only highlighted or not no matter if clicked or just hovered"""
        if shape_idx > -1:
            self.labels[shape_idx].vertices.isHighlighted = True
            self.labels[shape_idx].vertices.selectedVertex = vertex_idx

    def resetHighlight(self):
        for label in self.labels:
            label.isHighlighted = False
            label.vertices.isHighlighted = False

    def resetSelection(self):
        for label in self.labels:
            label.isSelected = False
            label.vertices.selectedVertex = -1

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

