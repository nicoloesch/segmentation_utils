from PyQt5 import QtWidgets
from PyQt5 import QtCore
from typing import Iterable


class Toolbar(QtWidgets.QToolBar):
    def __init__(self, parent):
        super(Toolbar, self).__init__(parent)
        self.actionsDict = {}  # This is a lookup table to match the buttons to the numbers they got added

        self.setMinimumSize(QtCore.QSize(80, 100))
        self.setMaximumSize(QtCore.QSize(80, 16777215))
        self.setAutoFillBackground(False)
        self.setStyleSheet("background-color: rgb(186, 189, 182);")
        self.setMovable(False)
        self.setAllowedAreas(QtCore.Qt.ToolBarArea.LeftToolBarArea)
        self.setOrientation(QtCore.Qt.Orientation.Vertical)
        self.setLayoutDirection(QtCore.Qt.LayoutDirection.LeftToRight)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.DefaultContextMenu)
        self.setObjectName("toolBar")

    def initMargins(self):
        """This function is necessary because the call to addToolBar in label_ui.py alters the alignment
        for some reason. Therefore this method will be called AFTER the toolbar is added to the main window"""
        m = (0, 0, 0, 0)
        self.setContentsMargins(*m)
        self.layout().setSpacing(2)
        self.layout().setContentsMargins(*m)

    def addAction(self, action):
        if isinstance(action, QtWidgets.QWidgetAction):
            return super(Toolbar, self).addAction(action)
        btn = QtWidgets.QToolButton()
        btn.setDefaultAction(action)
        btn.setToolButtonStyle(self.toolButtonStyle())
        btn.setMinimumSize(80, 70)
        btn.setMaximumSize(80, 70)
        self.addWidget(btn)

        actionText = action.text().replace('\n', '')
        self.actionsDict[actionText] = len(self.actionsDict)

        """
        # center align
        for i in range(self.layout().count()):
            if isinstance(
                self.layout().itemAt(i).widget(), QtWidgets.QToolButton
            ):
                self.layout().itemAt(i).setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        """

    def addActions(self, actions: Iterable[QtWidgets.QAction]) -> None:
        for action in actions:
            if action is None:
                self.addSeparator()
            else:
                self.addAction(action)

    def contextMenuEvent(self, event) -> None:
        if "DrawPolygon" in self.actionsDict:
            if self.actionGeometry(self.actions()[self.actionsDict["DrawPolygon"]]).contains(event.pos()):
                # TODO: raise own context menu with options for drawing a circle or a rectangle
                pass


