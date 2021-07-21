import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QListWidgetItem
from PyQt5.QtGui import QPixmap, QIcon

from seg_utils.utils.database import SQLiteDatabase
from seg_utils.ui.toolbar import Toolbar
from seg_utils.src.actions import Action
from seg_utils.ui.label_ui import LabelUI

import pathlib

IMAGES_DIR = "images/"


class SegLabelMain(QMainWindow, LabelUI):
    def __init__(self):
        super(SegLabelMain, self).__init__()
        self.setupUI(self)

        # placeholder variables that can be used later
        self.database = None
        self.basedir = None
        self.labeled_images = []
        self.current_label = []
        self.classes = []
        self.isLabeled = None
        self.img_idx = 0

        # File dialog options
        FDStartingDirectory = '/home/nico/isys/data'  # QDir.homePath()
        FDOptions = QFileDialog.DontUseNativeDialog

        # Define Actions
        actionOpenDB = Action(self,
                              "Open\nDatabase",
                              lambda: self.openDatabase(FDStartingDirectory, FDOptions),
                              'Ctrl+O',
                              "open",
                              "Open database",
                              enabled=True)
        actionSave = Action(self,
                            "Save",
                            self.saveLabel,
                            'Ctrl+S',
                            "save",
                            "Save Current State")
        actionNextImage = Action(self,
                                 "Next\nImage",
                                 self.nextImage,
                                 'Right',
                                 "next",
                                 "Go to next Image")
        actionPrevImage = Action(self,
                                 "Previous\nImage",
                                 self.prevImag,
                                 'Left',
                                 "prev",
                                 "Go to previos Image")
        actionDrawPoly = Action(self,
                                "Draw\nPolygon",
                                self.drawPoly,
                                icon="next",
                                tip="Draw Polygon (right click to show options)")
        actionTraceOutline = Action(self,
                                    "Draw\nPolygon",
                                    self.traceOutline,
                                    icon="outline",
                                    tip="Trace Outline")

        actionDrawCircle = Action(self,
                                  "Draw\nCircle",
                                  self.drawCircle,
                                  icon="circle",
                                  tip="Draw Circle")

        actionDrawSquare = Action(self,
                                  "Draw\nSquare",
                                  self.drawSquare(),
                                  icon="square",
                                  tip="Draw Square")

        # Init Toolbar
        self.toolBar.addAction(actionOpenDB)
        self.toolBar.addAction(actionSave)
        self.toolBar.addAction(actionNextImage)
        self.toolBar.addAction(actionPrevImage)
        self.toolBar.addAction(actionDrawPoly)
        self.toolBar.addAction(actionTraceOutline)

    def initWithDatabase(self, database: str):
        self.basedir = pathlib.Path(database).parents[0]
        self.database = SQLiteDatabase(database)
        self.labeled_images, self.isLabeled = self.database.get_labeled_images()
        self.initClasses()
        self.initFileList()
        self.updateImage()
        self.enableButtons(True)

    def initClasses(self):
        """This function initializes the availabe classes in the database and updates the label list"""
        self.classes = self.database.get_label_classes()
        for _class in self.classes:
            self.labelList.addItem(_class)

    def openDatabase(self, fddirectory, fdoptions):
        """This function is the handle for opening a database"""
        database, _ = QFileDialog.getOpenFileName(self,
                                                  caption="Select Database",
                                                  directory=fddirectory,
                                                  filter="Database (*.db)",
                                                  options=fdoptions)
        if database:
            self.initWithDatabase(database)
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
        self.polyList.clear()
        for lbl in self.current_label:
            self.polyList.addItem(lbl['label'])

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
            self.centerFrame.height(), Qt.KeepAspectRatio)

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
        for act in self.toolBar.actions():
            act.setEnabled(True)

    def drawPoly(self):
        four = 4

    def drawCircle(self):
        four = 4

    def drawSquare(self):
        four = 4

    def traceOutline(self):
        four = 4

    def saveLabel(self):
        four = 4