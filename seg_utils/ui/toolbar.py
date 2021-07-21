from PyQt5 import QtWidgets
from PyQt5 import QtCore


class Toolbar(QtWidgets.QToolBar):
    def __init__(self, title: str):
        super(Toolbar, self).__init__(title)
        layout = self.layout()
        m = (0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setContentsMargins(*m)
        self.setContentsMargins(*m)

        self.setMinimumSize(QtCore.QSize(80, 100))
        self.setMaximumSize(QtCore.QSize(80, 16777215))
        self.setBaseSize(QtCore.QSize(80, 0))
        self.setAutoFillBackground(False)
        self.setStyleSheet("background-color: rgb(186, 189, 182);")
        self.setMovable(False)
        self.setAllowedAreas(QtCore.Qt.LeftToolBarArea)
        self.setOrientation(QtCore.Qt.Vertical)
        self.etToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

    def addAction(self, action):
        if isinstance(action, QtWidgets.QWidgetAction):
            return super(Toolbar, self).addAction(action)
        btn = QtWidgets.QToolButton()
        btn.setDefaultAction(action)
        btn.setToolButtonStyle(self.toolButtonStyle())
        self.addWidget(btn)

        # center align
        for i in range(self.layout().count()):
            if isinstance(
                self.layout().itemAt(i).widget(), QtWidgets.QToolButton
            ):
                self.layout().itemAt(i).setAlignment(QtCore.Qt.AlignCenter)
