import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QListWidgetItem
from PyQt5.QtGui import QPixmap, QIcon


from seg_utils.utils.database import SQLiteDatabase
from seg_utils.utils import qt
from seg_utils.ui.toolbar import Toolbar
from seg_utils.src.actions import Action
from seg_utils.ui.label_ui import LabelUI
from seg_utils.ui.shape import Shape


import pathlib

IMAGES_DIR = "images/"


class LabelMain(QMainWindow, LabelUI):
    sigLabelSelected = pyqtSignal(int)

    def __init__(self):
        super(LabelMain, self).__init__()
        self.setupUI(self)

        # placeholder variables that can be used later
        self.database = None
        self.basedir = None
        self.labeled_images = []
        self.current_label = []
        self.classes = {}
        self.isLabeled = None
        self.img_idx = 0

        # color stuff
        self._num_colors = 25  # number of colors
        self.colorMap = None

        self._FD_Dir = '/home/nico/isys/data'  # QDir.homePath()
        self._FD_Opt = QFileDialog.DontUseNativeDialog
        self.initActions()
        self.connectEvents()

    def initActions(self):
        """Initialise all actions present which can be connected to buttons or menu items"""
        # TODO: some shortcuts dont work
        actionOpenDB = Action(self,
                              "Open\nDatabase",
                              lambda: self.openDatabase(self._FD_Dir, self._FD_Opt),
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
                                icon="polygon",
                                tip="Draw Polygon (right click to show options)")
        actionTraceOutline = Action(self,
                                    "Trace\nOutline",
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
        self.toolBar.addActions((actionOpenDB,
                                actionSave,
                                actionNextImage,
                                actionPrevImage,
                                actionDrawPoly,
                                actionTraceOutline))

    def connectEvents(self):
        self.fileList.itemClicked.connect(self.handleFileListItemClicked)
        self.fileSearch.textChanged.connect(self.handleFileListSearch)
        self.polyList.itemClicked.connect(self.handlePolyListSelection)
        self.imageDisplay.canvas.sigRequestLabelListUpdate.connect(self.handleUpdatePolyList)
        self.imageDisplay.canvas.sigRequestFitInView.connect(self.imageDisplay.fitInView)
        self.imageDisplay.scene.sigShapeHovered.connect(self.imageDisplay.canvas.handleShapeHovered)
        self.imageDisplay.scene.sigShapeSelected.connect(self.imageDisplay.canvas.handleShapeSelected)
        self.sigLabelSelected.connect(self.imageDisplay.canvas.handleShapeSelected)

    def initWithDatabase(self, database: str):
        """This function is called if a correct database is selected"""
        self.basedir = pathlib.Path(database).parents[0]
        self.database = SQLiteDatabase(database)
        self.labeled_images, self.isLabeled = self.database.get_labeled_images()
        self.imageDisplay.setInitialized()
        self.initColors()
        self.initClasses()
        self.initFileList()
        self.updateImage()
        self.enableButtons(True)

    def initClasses(self):
        """This function initializes the available classes in the database and updates the label list"""
        classes = self.database.get_label_classes()
        for idx, _class in enumerate(classes):
            item = qt.createListWidgetItemWithSquareIcon(_class, self.colorMap[idx], 10)
            self.labelList.addItem(item)
            self.classes[_class] = idx

    def initColors(self):
        r"""Initialise the colors for plotting and for the individual lists """
        self.colorMap, drawNewColor = qt.colormapRGB(n=self._num_colors)  # have a buffer for new classes
        self.imageDisplay.canvas.setNewColor(drawNewColor)

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

    def handleFileListItemClicked(self):
        """Tracks the changed item in the label List"""
        selected_file = self.fileList.currentItem().text()
        self.img_idx = self.labeled_images.index(IMAGES_DIR + selected_file)
        self.updateImage()

    def handleFileListSearch(self):
        r"""Handles the file search. If the user types into the text box, it changes the files which are displayed"""
        text = self.fileSearch.toPlainText()
        for item_idx in range(self.fileList.count()):
            if text not in self.fileList.item(item_idx).text():
                self.fileList.item(item_idx).setHidden(True)
            else:
                self.fileList.item(item_idx).setHidden(False)

    def updateLabel(self):
        """Updates the current displayed label/canvas"""
        labels = self.database.get_label_from_imagepath(self.labeled_images[self.img_idx])
        self.current_label = [Shape.from_dict(Shape(), _label,
                                              line_color=self.getColorForLabel(_label['label'])
                                              ) for _label in labels]
        self.polyList.updateList(self.current_label)

    def handleUpdatePolyList(self, _item_idx):
        for _idx in range(self.polyList.count()):
            self.polyList.item(_idx).setSelected(False)
        if _item_idx > -1:
            self.polyList.item(_item_idx).setSelected(True)

    def handlePolyListSelection(self, item):
        r"""Returns the row index within the list such that the plotter in canvas can update it"""
        self.sigLabelSelected.emit(self.polyList.row(item))

    def getColorForLabel(self, label_name):
        r"""Get a Color based on a label_name"""
        label_index = self.classes[label_name]
        return self.colorMap[label_index]

    def initFileList(self, show_check_box=False):
        r"""Initialize the file list with all the entries found in the database"""
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
        image = QPixmap(str(self.basedir / self.labeled_images[self.img_idx]))
        self.imageDisplay.canvas.setPixmap(image)
        self.imageDisplay.canvas.setLabels(self.current_label)
        self.fileList.setCurrentRow(self.img_idx)

    def nextImage(self):
        """Display the next image"""
        self.img_idx = (self.img_idx + 1) % len(self.labeled_images)
        self.updateImage()

    def prevImag(self):
        """Display the previous image"""
        self.img_idx = (self.img_idx - 1) % len(self.labeled_images)
        self.updateImage()

    def enableButtons(self, value: bool):
        """This function enables/disabled all the buttons as soon as there is a valid database selected.
            :param bool value: True enables Buttons, False disables them
        """
        for act in self.toolBar.actions():
            self.toolBar.widgetForAction(act).setEnabled(value)

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