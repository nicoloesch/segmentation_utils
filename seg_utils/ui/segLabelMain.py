from seg_utils.ui.segViewer import Ui_MainWindow
from PyQt5.QtCore import QDir, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QStyle)
from PyQt5.QtGui import QPixmap
from seg_utils.utils.database import SQLiteDatabase
import pathlib


class SegLabelMain(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(SegLabelMain, self).__init__()
