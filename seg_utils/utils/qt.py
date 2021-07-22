import os.path as osp
from PyQt5.QtGui import QIcon


def getIcon(icon):
    thisFile = osp.dirname(osp.abspath(__file__))
    icons_dir = osp.join(thisFile, "../icons")
    return QIcon(osp.join(":/", icons_dir, "%s.png" % icon))