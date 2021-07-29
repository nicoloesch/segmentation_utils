from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QColor, QPainter


class Shape(QGraphicsItem):
    def __init__(self,
                 label: str=None,
                 points=None,
                 line_color: QColor = None,
                 shape_type=None,
                 flags=None,
                 group_id=None,):
        super(Shape, self).__init__()
        self.label = label
        self.shape_type = shape_type
        self.points = points
        self.flags = flags
        self.group_id = group_id
        self.line_color, self.brush_color = None, None

    def __repr__(self):
        return f"Shape {self.label.capitalize()}"

    def initColor(self, color: QColor):
        self.line_color, self.brush_color = color, color.setAlphaF(0.5)

    def from_dict(self, label_dict: dict, line_color: QColor):
        r"""Method to create a Shape from a dict, which is stored in the SQL database"""
        if 'label' in label_dict:
            self.label = label_dict['label']
        if 'points' in label_dict:
            self.points = label_dict['points']
        if 'shape_type' in label_dict:
            self.shape_type = label_dict['shape_type']
        if 'flags' in label_dict:
            self.flags = label_dict['flags']
        if 'group_id' in label_dict:
            self.group_id = label_dict['group_id']

        self.initColor(line_color)
        return self



    def to_dict(self):
        r"""Method to store the current shape in the SQL Database"""
        pass

    def paint(self, painter: QPainter) -> None:
        """This paints the shape onto the canvas where it is called"""

