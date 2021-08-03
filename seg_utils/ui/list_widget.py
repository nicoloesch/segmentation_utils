from PyQt5 import QtWidgets
from PyQt5 import QtCore
from seg_utils.ui.shape import Shape
from seg_utils.utils.qt import createListWidgetItemWithSquareIcon

from typing import List, Union


class ListWidget(QtWidgets.QListWidget):
    def __init__(self, *args):
        super(ListWidget, self).__init__(*args)
        self._icon_size = 10
        #self.setSelectionMode(QtCore.Qt.ItemSelectionMo)

    def updateList(self, current_label: List[Shape]):
        self.clear()
        for lbl in current_label:
            txt = lbl.label
            col = lbl.line_color
            item = createListWidgetItemWithSquareIcon(txt, col, self._icon_size)
            self.addItem(item)

