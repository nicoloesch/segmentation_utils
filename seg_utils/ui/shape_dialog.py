from PyQt5.QtWidgets import QDialog, QPushButton, QWidget, QLabel, QVBoxLayout, QTextEdit, QHBoxLayout, QDialogButtonBox
from PyQt5.QtCore import QSize, QPoint
from PyQt5.QtGui import QFont

from seg_utils.ui.list_widget import ListWidget
from seg_utils.utils.qt import createListWidgetItemWithSquareIcon


class NewShapeDialog(QDialog):
    def __init__(self, parent: QWidget, *args):
        super(NewShapeDialog, self).__init__(*args)

        # Default values
        self.class_name = ""

        # Create the shape of the QDialog
        self.setFixedSize(QSize(300, 400))
        self.moveToCenter(parent.pos(), parent.size())
        self.setWindowTitle("Select class of new shape")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Textedit
        shapeText = QTextEdit(self)
        font = QFont()
        font.setPointSize(10)
        font.setKerning(True)
        shapeText.setFont(font)
        shapeText.setPlaceholderText("Enter shape label")
        shapeText.setMaximumHeight(25)

        # Buttons
        buttonWidget = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonWidget.button(QDialogButtonBox.Ok).clicked.connect(self.on_ButtonClicked)
        buttonWidget.button(QDialogButtonBox.Cancel).clicked.connect(self.on_ButtonClicked)

        # List of labels
        self.listWidget = ListWidget(self)
        self.listWidget.itemClicked.connect(self.on_ListSelection)

        # Combining everything
        layout.addWidget(shapeText)
        layout.addWidget(buttonWidget)
        layout.addWidget(self.listWidget)

        # Fill the listWidget
        for idx, _class in enumerate(parent.classes):
            item = createListWidgetItemWithSquareIcon(_class, parent.colorMap[idx], 10)
            self.listWidget.addItem(item)

    def moveToCenter(self, parent_pos: QPoint, parent_size: QSize):
        r"""Moves the QDialog to the center of the parent Widget.
        As self.move moves the upper left corner to the place, one needs to subtract the own size of the window"""
        self.move(parent_pos.x() + parent_size.width()/2 - self.size().width()/2,
                  parent_pos.y() + parent_size.height()/2 - self.size().height()/2)

    def on_ListSelection(self, item):
        self.class_name = item.text()

    def on_ButtonClicked(self):
        self.close()
