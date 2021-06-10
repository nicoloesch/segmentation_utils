
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QMainWindow,QWidget, QPushButton, QAction, QGridLayout,
                             QApplication, QFileDialog, QHBoxLayout, QLabel,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QGridLayout)
from PyQt5.QtGui import QIcon
import sys
import pathlib
from utils.database import SQLiteDatabase


class SegmentationUI(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Segmentation Tool")
        self.resize(1200, 1000)

        # General
        self.database = None
        self.basedir = None

        # Layouting
        # Todo: add the image displayer for the image display of the labeled image
        # Todo: add option/ button to go back to the labeled image instead of the video
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        outerLayout = QGridLayout()
        optionsLayout = QHBoxLayout()
        videoLayout = QVBoxLayout()
        controlLayout = QHBoxLayout()

        # OptionsWidget
        self.openImageFolderButton = QPushButton("Open\nLabels")
        self.openImageFolderButton.setIcon(self.style().standardIcon(QStyle.SP_DirIcon))
        self.openImageFolderButton.clicked.connect(self.openFolder)
        self.nextImageButton = QPushButton("Next\nImage")
        self.nextImageButton.setEnabled(False)
        self.nextImageButton.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        self.prevImageButton = QPushButton("Previous\nImage")
        self.prevImageButton.setEnabled(False)
        self.prevImageButton.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))

        optionsLayout.addWidget(self.openImageFolderButton)
        optionsLayout.addWidget(self.prevImageButton, 1)
        optionsLayout.addWidget(self.nextImageButton, 2)

        # Video
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        videoWidget = QVideoWidget()
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

        # Error Widget
        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                                      QSizePolicy.Maximum)

        # Controls for the Video
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.prevFrameButton)
        controlLayout.addWidget(self.nextFrameButton)

        videoLayout.addWidget(videoWidget)
        videoLayout.setContentsMargins(0, 0, 0, 0)
        videoLayout.addWidget(self.positionSlider)
        videoLayout.addLayout(controlLayout)
        videoLayout.addWidget(self.errorLabel)

        # Set the layout on the application's window
        outerLayout.addLayout(optionsLayout, 1, 0)
        outerLayout.addWidget(videoWidget, 0, 1)
        outerLayout.addLayout(videoLayout, 0, 1, 2, 1)
        mainWidget.setLayout(outerLayout)

        # Set the State of the mediaplayer
        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def openFolder(self):
        labeldir = QFileDialog.getExistingDirectory(self, "Select Folder Containing Images",
                                                    QDir.homePath())
        self.basedir = pathlib.Path(labeldir).parents[0]
        # TODO: Find Database function that generates an error or something
        self.database = SQLiteDatabase(self.homedir, "database.db")


        #TODO: display first labeled image of the labels folder and the corresponding raw image and video at current frame

        four = 4
        """
        if fileName != '':
            self.mediaPlayer.setMedia(
                QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
        """
    #def exitCall(self):
        #sys.exit(app.exec_())

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
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        layout = QVBoxLayout()
        layout.addWidget(videoWidget)
        layout.addLayout(controlLayout)
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