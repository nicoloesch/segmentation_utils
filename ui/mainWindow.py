from PyQt5.QtCore import QDir, Qt, QUrl, QPointF
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QMainWindow, QAction, QTextEdit,
                             QApplication, QFileDialog, QHBoxLayout, QLabel, QStackedWidget,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QGridLayout)
from PyQt5.QtGui import QPixmap, QPolygonF
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

# TODO: replace with open database rather than the images as the databse contains all necessary information
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
        self.videoRangeMS = 2000
        self._begin = None
        self._end = None
        self._videoDuration = None
        self.fps = 25.0
        self.frameRate = (1.0/self.fps)*1000.0  # duration of one frame in ms
        self.labelFrame = None
        self.label_names = {"_background_": 0}  # TODO: remove that and replace by table in SQL

        # Layouting
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
        self.labelImage = QLabel(self)
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.labelwidget = QStackedWidget()
        self.labelwidget.addWidget(self.labelImage)
        self.labelVideo = QVideoWidget()
        self.labelwidget.addWidget(self.labelVideo)
        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.nextFrameButton = QPushButton()
        self.nextFrameButton.setEnabled(False)
        self.nextFrameButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.nextFrameButton.clicked.connect(self.nextFrame)

        self.prevFrameButton = QPushButton()
        self.prevFrameButton.setEnabled(False)
        self.prevFrameButton.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.prevFrameButton.clicked.connect(self.prevFrame)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.displayLabelButton = QPushButton("Label")
        self.displayLabelButton.setEnabled(False)
        self.displayLabelButton.clicked.connect(self.displayLabel)

        self.initVideo()

        # TODO: Painter for drawing the raw polygons - has to be called somewhere else
        # self._painter = QPainter()

        # Error Widget
        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                                      QSizePolicy.Maximum)

        # Controls for the Video
        videoControlLayout.setContentsMargins(0, 0, 0, 0)
        videoControlLayout.addWidget(self.playButton)
        videoControlLayout.addWidget(self.prevFrameButton)
        videoControlLayout.addWidget(self.nextFrameButton)
        videoControlLayout.addWidget(self.displayLabelButton)

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
        # this makes sure only labeled images can be displayed as they are the only ones being in the SQL database
        self.labeled_images = self.database.get_entries_of_column('labels', 'image_path')
        self.updateImages()
        self.nextImageButton.setEnabled(True)
        self.prevImageButton.setEnabled(True)
        self.playButton.setEnabled(True)

    #def exitCall(self):
        #sys.exit(app.exec_())

    def updateImages(self):
        self.image.setPixmap(QPixmap(str(self.basedir / self.labeled_images[self.image_idx])))
        # TODO: replace with calls to the SQL database rather than the files themselves
        path_to_labelled = self.basedir / 'labels/SegmentationClassVisualization'
        filename_labeled = pathlib.Path(self.labeled_images[self.image_idx]).stem + '.jpg'
        self.labelImage.setPixmap(QPixmap(str(path_to_labelled / filename_labeled)))
        # label_list = LabelStruct.from_json(self.database.get_label_from_imagepath(self.labeled_images[self.image_idx]))

    """
    def drawLabel(self, labels: List[LabelStruct]):
        # TODO: Polygon drawer
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
    """

    def nextImage(self):
        if self.labelwidget.currentWidget() == self.labelVideo:
            self.labelwidget.setCurrentWidget(self.labelImage)
        self.image_idx = (self.image_idx + 1) % len(self.labeled_images)
        self.mediaPlayer.stop()
        self.setVideoControls(False)
        self.updateImages()

    def prevImage(self):
        self.image_idx = (self.image_idx + -1) % len(self.labeled_images)
        self.mediaPlayer.stop()
        self.setVideoControls(False)
        self.updateImages()

    def nextFrame(self):
        self.setPosition(self.mediaPlayer.position() + self.frameRate)

    def prevFrame(self):
        self.setPosition(self.mediaPlayer.position() - self.frameRate)

    def initVideo(self):
        self.mediaPlayer.mediaStatusChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.stateChanged.connect(self.stateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def play(self):
        if self.labelwidget.currentWidget() == self.labelImage:
            # display the video Widget if currently the label image is displayed
            self.labelwidget.setCurrentWidget(self.labelVideo)

        if self.mediaPlayer.state() == QMediaPlayer.StoppedState:
            self.setVideo()
            self.mediaPlayer.play()
            self.displayLabelButton.setEnabled(True)
        elif self.mediaPlayer.state() == QMediaPlayer.PausedState:
            # if the player has been in the paused state, the video starts playing again
            self.mediaPlayer.play()
            self.displayLabelButton.setEnabled(True)
            self.setSkipButtons(False)
        elif self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            # if the video has been playing (and the pause button got pressed) the video will pause
            self.displayLabelButton.setEnabled(True)
            self.setSkipButtons(True)
            self.mediaPlayer.pause()
        else:
            pass

    def stateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPause))
        elif state == QMediaPlayer.PausedState or state == QMediaPlayer.StoppedState:
            self.playButton.setIcon(
                self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            pass

    def mediaStateChanged(self, state):
        # NOTE: idk if that is right...
        if state == QMediaPlayer.EndOfMedia:
            self.setPosition(self._begin)
        elif state == QMediaPlayer.LoadedMedia:
            self.setStoppingPosition()

    def positionChanged(self, position):
        self.positionSlider.setValue(position)
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            if position > self._end or position < self._begin:
                self.setPosition(self._begin)

    def durationChanged(self, duration):
        self.positionSlider.setRange(self._begin, self._end)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def setStartingPosition(self):
        self._begin = max(0, self.frame_to_ms(self.labelFrame) - self.videoRangeMS / 2.0)
        self._end = min(self._videoDuration, self.frame_to_ms(self.labelFrame) + self.videoRangeMS / 2.0)

    def setVideo(self):
        # TODO: move to init?
        self.mediaPlayer.setVideoOutput(self.labelVideo)
        video, self.labelFrame, self._videoDuration = self.database.get_video_from_image(self.labeled_images[self.image_idx])
        self.mediaPlayer.setMedia(
            QMediaContent(QUrl.fromLocalFile(str(self.basedir / video))))
        self.setStartingPosition()
        self.setPosition(self._begin)
        self.playButton.setEnabled(True)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

    def setSkipButtons(self, value: bool):
        self.prevFrameButton.setEnabled(value)
        self.nextFrameButton.setEnabled(value)

    def displayLabel(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        self.labelwidget.setCurrentWidget(self.labelImage)
        self.setSkipButtons(False)
        self.displayLabelButton.setEnabled(False)
        self.updateImages()

    @staticmethod
    def frame_to_ms(frame_number: int, fps: int = 25):
        return (frame_number/fps) * 1000.0
