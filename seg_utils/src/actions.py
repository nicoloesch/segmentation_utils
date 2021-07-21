# This file is intended if the actions need to be modified
# Additionally, all actions will be already predefined here so one does not need QT Designer anymore

from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
import os.path as osp

thisFile = osp.dirname(osp.abspath(__file__))


class Action(QAction):
    """Create an Action"""
    def __init__(self,
                 parent,
                 text,
                 event=None,
                 shortcut=None,
                 icon=None,
                 tip=None,
                 checkable=False,
                 enabled=False,
                 checked=False,
                 ):
        super(Action, self).__init__(text, parent)
        if icon is not None:
            self.setIconText(text.replace(" ", "\n"))
            self.setIcon(self.getIcon(icon))
        if shortcut is not None:
            if isinstance(shortcut, (list, tuple)):
                self.setShortcuts(shortcut)
            else:
                self.setShortcut(shortcut)
        if tip is not None:
            self.setToolTip(tip)
            self.setStatusTip(tip)
        if event is not None:
            self.triggered.connect(event)
        if checkable:
            self.setCheckable(True)
        self.setEnabled(enabled)
        self.setChecked(checked)

    @staticmethod
    def getIcon(icon):
        icons_dir = osp.join(thisFile, "../icons")
        return QIcon(osp.join(":/", icons_dir, "%s.png" % icon))
