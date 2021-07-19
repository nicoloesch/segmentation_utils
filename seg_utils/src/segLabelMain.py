import sys


from PyQt5.QtCore import QDir, QUrl
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QStyle, QListWidgetItem, QGraphicsItem, QGraphicsScene
from PyQt5.QtGui import QPixmap, QIcon

from seg_utils.utils.database import SQLiteDatabase
from seg_utils.ui.segLabel import Ui_segLabeling
from seg_utils.resource.imageViewer import ImageViewer

import pathlib

IMAGES_DIR = "images/"


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
        self.fileList.itemClicked.connect(self.fileListItemChanged)
        self.fileSearch.textChanged.connect(self.fileListSearch)

    def openDatabase(self, fdoptions, fddirectory):
        """This function is the handle for opening a database"""
        database, _ = QFileDialog.getOpenFileName(self,
                                                  caption="Select Database",
                                                  directory=fddirectory,
                                                  filter="Database (*.db)",
                                                  options=fdoptions)
        if database:
            self.basedir = pathlib.Path(database).parents[0]
            self.database = SQLiteDatabase(database)
            self.labeled_images, self.isLabeled = self.database.get_labeled_images()
            self.initFileList()
            self.updateImage()
            self.enableButtons(True)
        else:
            # TODO: Exit on cancel - needs to be altered to something more useful
            sys.exit(1)

    def fileListItemChanged(self):
        """Tracks the changed item in the label List"""
        selected_file = self.fileList.currentItem().text()
        self.img_idx = self.labeled_images.index(IMAGES_DIR + selected_file)
        self.updateImage()

    def fileListSearch(self):
        text = self.fileSearch.toPlainText()
        #lbl_list = [x for x in self.labeled_images if text in x]
        for item_idx in range(self.fileList.count()):
            if text not in self.fileList.item(item_idx).text():
                self.fileList.item(item_idx).setHidden(True)
            else:
                self.fileList.item(item_idx).setHidden(False)

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
                                       self.labeled_images[idx].replace(IMAGES_DIR, ""))
            else:
                item = QListWidgetItem(self.labeled_images[idx].replace(IMAGES_DIR, ""))
            self.fileList.addItem(item)
        self.fileList.setCurrentRow(self.img_idx)

    def updateImage(self):
        """Updates the displayed image and respective label/canvas"""
        self.updateLabel()
        #self.scene.addPixmap(QPixmap(str(self.basedir / self.labeled_images[self.img_idx])).scaledToWidth(
        #    self.imageDisplay.width()))
        image = QPixmap(str(self.basedir / self.labeled_images[self.img_idx])).scaled(
            self.centerFrame.width(),
            self.centerFrame.height(),Qt.KeepAspectRatio)

        self.imageDisplay.setImage(image)
        self.fileList.setCurrentRow(self.img_idx)

    def nextImage(self):
        self.img_idx = (self.img_idx + 1) % len(self.labeled_images)
        self.updateImage()

    def prevImag(self):
        self.img_idx = (self.img_idx - 1) % len(self.labeled_images)
        self.updateImage()

    def enableButtons(self, value: bool):
        """This function enables/disabled all the buttons as soon as there is a valid database selected.
            :param bool value: True enables Buttons, False disables them
        """
        self.saveButton.setEnabled(value)
        self.nextImageButton.setEnabled(value)
        self.prevImageButton.setEnabled(value)
        self.createPolygonButton.setEnabled(value)
        self.traceOutlineButton.setEnabled(value)

    def createPoly(self):
        four = 4

    def traceOutline(self):
        four = 4

    def save(self):
        four = 4
