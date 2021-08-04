import sys

from PyQt5.QtCore import pyqtSignal, QPointF, QRectF, Qt
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QListWidgetItem, QDialog, QLabel
from PyQt5.QtGui import QPixmap, QIcon

from seg_utils.utils.database import SQLiteDatabase
from seg_utils.utils import qt
from seg_utils.ui.toolbar import Toolbar
from seg_utils.src.actions import Action
from seg_utils.ui.label_ui import LabelUI
from seg_utils.ui.shape import Shape
from seg_utils.ui.shape_dialog import NewShapeDialog

import pathlib

IMAGES_DIR = "images/"


class LabelMain(QMainWindow, LabelUI):
    sig_LabelSelected = pyqtSignal(int, int, int)
    CREATE, EDIT = 0, 1

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
        self.b_autoSave = True
        self.actions = tuple()
        self.actions_dict = {}

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
                              lambda: self.on_openDatabase(self._FD_Dir, self._FD_Opt),
                              'Ctrl+O',
                              "open",
                              "Open database",
                              enabled=True)
        actionSave = Action(self,
                            "Save",
                            self.on_saveLabel,
                            'Ctrl+S',
                            "save",
                            "Save current state to database")
        actionNextImage = Action(self,
                                 "Next\nImage",
                                 self.on_nextImage,
                                 'Right',
                                 "next",
                                 "Go to next image")
        actionPrevImage = Action(self,
                                 "Previous\nImage",
                                 self.on_prevImag,
                                 'Left',
                                 "prev",
                                 "Go to previous image")
        actionDrawPoly = Action(self,
                                "Draw\nPolygon",
                                self.on_drawPolygon,
                                icon="polygon",
                                tip="Draw Polygon (right click to show options)",
                                checkable=True)
        actionTraceOutline = Action(self,
                                    "Trace\nOutline",
                                    self.on_traceOutline,
                                    icon="outline",
                                    tip="Trace Outline",
                                    checkable=True)

        actionDrawCircle = Action(self,
                                  "Draw\nCircle",
                                  self.on_drawCircle,
                                  icon="circle",
                                  tip="Draw Circle",
                                  checkable=True)

        actionDrawRectangle = Action(self,
                                     "Draw\nRectangle",
                                     lambda: self.on_drawRectangle(QPointF(), QPointF()),
                                     icon="square",
                                     tip="Draw Rectangle",
                                     checkable=True)

        self.actions = ((actionOpenDB,
                         actionSave,
                         actionNextImage,
                         actionPrevImage,
                         actionDrawPoly,
                         actionTraceOutline,
                         actionDrawCircle,
                         actionDrawRectangle))
        # Init Toolbar
        self.toolBar.addActions(self.actions)

    def connectEvents(self):
        self.fileList.itemClicked.connect(self.handleFileListItemClicked)
        self.fileSearch.textChanged.connect(self.handleFileListSearch)
        self.polyList.itemClicked.connect(self.handlePolyListSelection)
        self.imageDisplay.canvas.sig_RequestLabelListUpdate.connect(self.handleUpdatePolyList)
        self.imageDisplay.canvas.sig_RequestFitInView.connect(self.imageDisplay.fitInView)
        self.imageDisplay.scene.sig_ShapeHovered.connect(self.imageDisplay.canvas.handleShapeHovered)
        self.imageDisplay.scene.sig_ShapeSelected.connect(self.imageDisplay.canvas.handleShapeSelected)
        self.sig_LabelSelected.connect(self.imageDisplay.canvas.handleShapeSelected)

        # Drawing Events
        self.imageDisplay.scene.sig_RectangleDrawing.connect(self.on_drawRectangle)
        self.imageDisplay.scene.sig_RectangleDone.connect(self.on_drawEnd)

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

    def handleUpdatePolyList(self, _item_idx):
        for _idx in range(self.polyList.count()):
            self.polyList.item(_idx).setSelected(False)
        if _item_idx > -1:
            self.polyList.item(_item_idx).setSelected(True)

    def handlePolyListSelection(self, item):
        r"""Returns the row index within the list such that the plotter in canvas can update it"""
        self.sig_LabelSelected.emit(self.polyList.row(item), self.polyList.row(item), -1)

    def getColorForLabel(self, label_name: str):
        r"""Get a Color based on a label_name"""
        label_index = self.classes[label_name]
        return self.colorMap[label_index]

    def updateImage(self):
        """Updates the displayed image and respective label/canvas"""
        self.updateLabel()
        image = QPixmap(str(self.basedir / self.labeled_images[self.img_idx]))
        self.imageDisplay.canvas.setPixmap(image)
        self.imageDisplay.canvas.setLabels(self.current_label)
        self.fileList.setCurrentRow(self.img_idx)

    def updateLabel(self):
        """Updates the current displayed label/canvas"""
        labels = self.database.get_label_from_imagepath(self.labeled_images[self.img_idx])
        self.current_label = [Shape.from_dict
                              (Shape(), _label, color=self.getColorForLabel(_label['label']))
                              for _label in labels]
        self.polyList.updateList(self.current_label)

    def enableButtons(self, value: bool):
        """This function enables/disabled all the buttons as soon as there is a valid database selected.
            :param bool value: True enables Buttons, False disables them
        """
        for act in self.toolBar.actions():
            self.toolBar.widgetForAction(act).setEnabled(value)

        # TODO: this disables the Open Database Button as i only need it once
        #   and currently it crashes everything if clicked again
        self.toolBar.getWidgetForAction('OpenDatabase').setEnabled(False)

    def on_openDatabase(self, fddirectory, fdoptions):
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

    def on_saveLabel(self):
        """Save current state to database"""
        four = 4

    def on_nextImage(self):
        """Display the next image"""
        self.img_idx = (self.img_idx + 1) % len(self.labeled_images)
        self.updateImage()

    def on_prevImag(self):
        """Display the previous image"""
        self.img_idx = (self.img_idx - 1) % len(self.labeled_images)
        self.updateImage()

    def on_drawPolygon(self):
        """Draw own Polygon"""
        four = 4

    def on_drawCircle(self):
        """Draw own Circle"""
        four = 4

    def on_drawRectangle(self, upper_left: QPointF = QPointF(), lower_right: QPointF = QPointF()):
        """Draw own Rectangle"""
        if self.toolBar.getWidgetForAction('DrawRectangle').isChecked():
            # Case for enabled drawing
            self.imageDisplay.scene.mode = self.CREATE
            if not upper_left.isNull() and not upper_left.isNull():
                rect = QRectF(upper_left, lower_right)
        else:
            self.imageDisplay.scene.mode = self.EDIT

    def on_drawEnd(self, upper_left: QPointF(), lower_right: QPointF):
        print("Drawing Ended")
        d = NewShapeDialog(self)
        d.exec()

        if d.class_name:
            shape = Shape(label=d.class_name, points=[upper_left, lower_right],
                          color=self.getColorForLabel(d.class_name), shape_type="rectangle")

    def on_traceOutline(self):
        """Trace the outline of a shape"""
        four = 4
