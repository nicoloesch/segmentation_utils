from seg_utils.ui.segLabel import Ui_segLabeling
from PyQt5.QtCore import QDir, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QStyle, QListWidgetItem
from PyQt5.QtGui import QPixmap, QIcon
from seg_utils.utils.database import SQLiteDatabase
import pathlib


class SegLabelMain(QMainWindow, Ui_segLabeling):
    def __init__(self):
        super(SegLabelMain, self).__init__()
        self.setupUi(self)

        # placeholder variables that can be used later
        self.database = None
        self.basedir = None
        self.labeled_images = None
        self.current_label = None
        self.isLabeled = None
        self.img_idx = 0

        # File Dialog Options
        FDStartingDirectory = '/home/nico/isys/data' # QDir.homePath()
        FDOptions = QFileDialog.DontUseNativeDialog

        # Connect all Buttons to Events
        self.openDatabaseButton.clicked.connect(lambda: self.openDatabase(FDOptions, FDStartingDirectory))
        self.nextImageButton.clicked.connect(self.nextImage)
        self.prevImageButton.clicked.connect(self.prevImag)
        self.createPolygonButton.clicked.connect(self.createPoly)
        self.traceOutlineButton.clicked.connect(self.traceOutline)
        self.saveButton.clicked.connect(self.save)

    def openDatabase(self, fdoptions, fddirectory):
        """This function is the handle for opening a database"""
        database, _ = QFileDialog.getOpenFileName(self,
                                                  caption="Select Database",
                                                  directory=fddirectory,
                                                  filter="Database (*.db)",
                                                  options=fdoptions)
        self.basedir = pathlib.Path(database).parents[0]
        self.database = SQLiteDatabase(database)
        self.labeled_images, self.isLabeled = self.database.get_labeled_images()
        self.initFileList()
        self.updateImage()

    def updateLabel(self):
        """Updates the current displayed label/canvas"""
        self.current_label = self.database.get_label_from_imagepath(self.labeled_images[self.img_idx])

    def updateFileList(self):
        """Updates the File List display"""
        four = 4

    def initFileList(self, show_check_box=False):
        for idx, elem in enumerate(self.labeled_images):
            if show_check_box:
                # TODO: relative path doesnt work
                item = QListWidgetItem(QIcon("./icons/checked.png"),
                                       self.labeled_images[idx].replace("images/", ""))
            else:
                item = QListWidgetItem(self.labeled_images[idx].replace("images/", ""))
            self.fileList.addItem(item)

    def updateImage(self):
        """Updates the displayed image and respective label/canvas"""
        self.updateLabel()
        self.imageDisplay.setPixmap(QPixmap(str(self.basedir / self.labeled_images[self.img_idx])).scaledToWidth(
            self.imageDisplay.width()))

    def nextImage(self):
        self.img_idx = (self.img_idx + 1) % len(self.labeled_images)
        self.updateImage()

    def prevImag(self):
        self.img_idx = (self.img_idx - 1) % len(self.labeled_images)
        self.updateImage()

    def createPoly(self):
        four = 4

    def traceOutline(self):
        four = 4

    def save(self):
        four = 4
