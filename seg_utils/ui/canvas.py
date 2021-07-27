from PyQt5.QtGui import QPainter, QBrush, QPen, QPolygonF
from seg_utils.src.image_viewer import ImageViewer
from PyQt5.QtCore import Qt, QPointF
from typing import List

# CURRENTLY DEPRECATED
# QPainter should only be spawned in the paintEvent of the widget in charge
# https://forum.qt.io/topic/64693/unable-to-paint-on-qt-widget-shows-error-paintengine-should-no-longer-be-called/2
# Could inherit from QWidget and then show them on top of each other with the position matched to QGraphicsView
class Canvas:
    def __init__(self, image_viewer: ImageViewer):
        self.four = 4
        self._painter = QPainter(image_viewer)

    def drawPolygon(self, points: List[QPointF]):
        if not isinstance(points[0], QPointF):
            points = [self.list_to_QPoint(_point) for _point in points]
        polygon = QPolygonF(points)
        self._painter.setPen(QPen(Qt.white, 5, Qt.SolidLine))
        self._painter.drawPolygon(polygon)

    @staticmethod
    def list_to_QPoint(coordinate):
        assert len(coordinate) == 2
        return QPointF(*coordinate)