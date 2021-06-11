from PyQt5.QtCore import QDir, Qt, QUrl, QPointF
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QMainWindow, QAction, QTextEdit,
                             QApplication, QFileDialog, QHBoxLayout, QLabel, QStackedWidget,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QGridLayout)
from PyQt5.QtGui import QIcon, QPixmap, QPolygonF, QPainter, QColor, QBrush, QPen

import sys
import pathlib
import base64
from typing import List

from utils.database import SQLiteDatabase, LabelStruct
from utils import images

import PIL.Image
import imgviz

COLOR_LIST = [Qt.red,
              Qt.cyan,
              Qt.yellow,
              Qt.red,
              Qt.green,
              Qt.magenta,
              Qt.darkBlue,
              Qt.darkCyan,
              Qt.darkYellow,
              Qt.darkRed,
              Qt.darkGreen,
              Qt.darkMagenta]


class SegmentationUI(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Segmentation Tool")
        self.resize(1200, 1000)

        # General
        self.database = None
        self.basedir = None
        self.labeled_images = None
        self.image_idx = 0
        self.label_names = {"_background_": 0}  # TODO: remove that and replace by table in SQL

        # Layouting
        # Todo: add option/ button to go back to the labeled image instead of the video
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        outerLayout = QGridLayout()

        # It is a 2x2 grid Layout which has in the top left hand corner the raw image with the controls
        # below are potential notes, top right hand corner is the labeled image/ video with the controls of the video
        # and bottom right hand corner is the label list of all present labels

        # --------------------
        # Raw Image - Top Left
        # --------------------
        imageLayout = QVBoxLayout()
        optionsLayout = QHBoxLayout()
        # Image
        self.image = QLabel(self)

        # OptionsWidget
        self.openImageFolderButton = QPushButton("Open\nLabels")
        self.openImageFolderButton.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
        self.openImageFolderButton.clicked.connect(self.openFolder)
        self.nextImageButton = QPushButton("Next\nImage")
        self.nextImageButton.setEnabled(False)
        self.nextImageButton.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        self.nextImageButton.clicked.connect(self.nextImage)
        self.prevImageButton = QPushButton("Previous\nImage")
        self.prevImageButton.setEnabled(False)
        self.prevImageButton.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
        self.prevImageButton.clicked.connect(self.prevImage)

        optionsLayout.addWidget(self.openImageFolderButton)
        optionsLayout.addWidget(self.prevImageButton)
        optionsLayout.addWidget(self.nextImageButton)

        # Final Layouting for this one cell
        imageLayout.addWidget(self.image)
        imageLayout.addLayout(optionsLayout)

        # --------------------
        # Notes - Bottom Left
        # --------------------
        notesLayout = QVBoxLayout()
        notesLabel = QLabel("Type Notes in here", self)

        textbox = QTextEdit(self,
                            lineWrapMode=QTextEdit.FixedColumnWidth,
                            lineWrapColumnOrWidth=50,
                            placeholderText="Type your notes in here",
                            readOnly=False,
                            )
        notesLayout.addWidget(notesLabel)
        notesLayout.addWidget(textbox)

        # --------------------
        # Video/ Image - Top Right
        # --------------------
        labelLayout = QVBoxLayout()
        videoControlLayout = QHBoxLayout()
        self.label_image = QLabel(self)
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.labelwidget = QStackedWidget()
        self.labelwidget.addWidget(self.label_image)
        self.labelwidget.addWidget(QVideoWidget())
        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.nextFrameButton = QPushButton()
        self.nextFrameButton.setEnabled(False)
        self.nextFrameButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))

        self.prevFrameButton = QPushButton()
        self.prevFrameButton.setEnabled(False)
        self.prevFrameButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekBackward))

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.displayLabelButton = QPushButton("Display\nLabel")
        self.displayLabelButton.setEnabled(False)

        #TODO: call painter somewhere else
        self._painter = QPainter()

        # Error Widget
        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                                      QSizePolicy.Maximum)

        # Controls for the Video
        videoControlLayout.setContentsMargins(0, 0, 0, 0)
        videoControlLayout.addWidget(self.playButton)
        videoControlLayout.addWidget(self.prevFrameButton)
        videoControlLayout.addWidget(self.nextFrameButton)

        labelLayout.setContentsMargins(0, 0, 0, 0)
        labelLayout.addWidget(self.labelwidget)
        labelLayout.addWidget(self.positionSlider)
        labelLayout.addLayout(videoControlLayout)
        labelLayout.addWidget(self.errorLabel)

        # --------------------
        # Final - Put everything to the outerlayout
        # --------------------
        outerLayout.addLayout(imageLayout, 0, 0)
        outerLayout.addLayout(notesLayout, 1, 0)
        outerLayout.addLayout(labelLayout, 0, 1, 2, 1)
        mainWidget.setLayout(outerLayout)

    def openFolder(self):
        labeldir = QFileDialog.getExistingDirectory(self, "Select Folder Containing Images",
                                                    QDir.homePath())
        self.basedir = pathlib.Path(labeldir).parents[0]
        self.database = SQLiteDatabase(str(self.basedir), "database.db")
        self.labeled_images = self.database.get_entries_of_column('labels', 'image_path')
        self.updateImages()
        self.nextImageButton.setEnabled(True)
        self.prevImageButton.setEnabled(True)
        self.playButton.setEnabled(True)
        """
        if fileName != '':
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(fileName)))
            
        """

    #def exitCall(self):
        #sys.exit(app.exec_())

    def updateImages(self):
        self.image.setPixmap(QPixmap(str(self.basedir / self.labeled_images[self.image_idx])))
        self.label_image.setPixmap(QPixmap(str(self.basedir / self.labeled_images[self.image_idx])))
        label_list = LabelStruct.from_json(self.database.get_label_from_imagepath(self.labeled_images[self.image_idx]))
        self.drawLabel(label_list)

    def drawLabel(self, labels: List[LabelStruct]):
        # TODO: so far only polygons can be drawn
        imagePath = str(self.basedir / self.labeled_images[self.image_idx])
        s = []
        for _label in labels:
            points = QPolygonF([QPointF(point[0], point[1]) for point in _label.points])
            label_name = _label.label_name
            if label_name not in self.label_names:
                self.label_names[label_name] = len(self.label_names)
            self.PainterInstance.setPen(QPen(COLOR_LIST[self.label_names[label_name]], 5, Qt.SolidLine))
            self.PainterInstance.drawPolygon(points)
            # TODO: Canvas Class as in labelme
            #  https://github.com/wkentaro/labelme/blob/115816d3e47c80f64e843085fb09cf878ce19dfa/labelme/widgets/canvas.py

            
    def nextImage(self):
        self.image_idx = (self.image_idx + 1) % len(self.labeled_images)
        self.updateImages()

    def prevImage(self):
        self.image_idx = (self.image_idx + -1) % len(self.labeled_images)
        self.updateImages()

    def setVideoState(self):
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())


        """
        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Maximum)

        # Create new action
        openAction = QAction(QIcon('open.png'), '&Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.setStatusTip('Open movie')
        openAction.triggered.connect(self.openFile)

        # Create exit action
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.exitCall)

        # Create menu bar and add action
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        #fileMenu.addAction(newAction)
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

        # Create a widget for window contents
        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Create layouts to place inside widget
        videoControlLayout = QHBoxLayout()
        videoControlLayout.setContentsMargins(0, 0, 0, 0)
        videoControlLayout.addWidget(self.playButton)
        videoControlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(videoControlLayout)
        layout.addWidget(self.errorLabel)

        # Set widget to contain window contents
        wid.setLayout(layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                QDir.homePath())

        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)

    def exitCall(self):
        sys.exit(app.exec_())

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())
"""