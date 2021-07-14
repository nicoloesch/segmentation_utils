from ui.SegmentationAnalysis import Ui_MainWindow
from PyQt5.QtCore import QDir, Qt, QUrl, QPointF
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QMainWindow, QAction, QTextEdit,
                             QApplication, QFileDialog, QHBoxLayout, QLabel, QStackedWidget,
                             QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QGridLayout)
from PyQt5.QtGui import QPixmap, QPolygonF
from utils.database import SQLiteDatabase
import pathlib


class SegAnalysisMain(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(SegAnalysisMain, self).__init__()
        self.setupUi(self)
        self.database = None
        self.basedir = None
        self.labeled_images = None
        self.label_classes = None
        self.labelFrame = None
        self.image_idx = 0
        self.videoRangeMS = 2000
        self._begin = None
        self._end = None
        self._videoDuration = None
        self.fps = 25.0
        self.frameDurationMS = (1.0/self.fps)*1000.0  # duration of one frame in ms

        # Other resources for various elements
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.setNotifyInterval(50)

        # Connect all buttons to events
        self.openDatabaseButton.clicked.connect(self.openDatabase)
        self.nextImageButton.clicked.connect(self.nextImage)
        self.prevImageButton.clicked.connect(self.prevImage)
        self.playButton.clicked.connect(self.playVideo)
        self.nextFrameButton.clicked.connect(self.nextFrame)
        self.prevFrameButton.clicked.connect(self.prevFrame)
        self.displayLabelButton.clicked.connect(self.displayLabel)

    def openDatabase(self):
        database, _ = QFileDialog.getOpenFileName(self,
                                                  caption="Select Database",
                                                  directory=QDir.homePath(),
                                                  filter="Database (*.db)",
                                                  options=QFileDialog.DontUseNativeDialog)
        self.basedir = pathlib.Path(database).parents[0]
        self.database = SQLiteDatabase(database)
        self.labeled_images = self.database.get_entries_of_column('labels', 'image_path')
        self.updateImages()
        self.initButtons()
        self.initVideo()
        self.setNotesOfUI()

    def nextImage(self):
        self.getNotesFromUI()
        if self.stackedWidget.currentWidget() == self.videoWidget:
            self.stackedWidget.setCurrentWidget(self.labelImageWidget) # maybe self.labelImage insteada
        self.image_idx = (self.image_idx + 1) % len(self.labeled_images)
        self.setNotesOfUI()
        self.mediaPlayer.stop()
        self.setSkipButtons(False)
        self.updateImages()

    def prevImage(self):
        self.getNotesFromUI()
        if self.stackedWidget.currentWidget() == self.videoWidget:
            self.stackedWidget.setCurrentWidget(self.labelImageWidget) # maybe self.labelImage insteada
        self.image_idx = (self.image_idx + -1) % len(self.labeled_images)
        self.setNotesOfUI()
        self.mediaPlayer.stop()
        self.setSkipButtons(False)
        self.updateImages()

    def nextFrame(self):
        self.setPosition(self.mediaPlayer.position() + self.frameDurationMS)

    def prevFrame(self):
        self.setPosition(self.mediaPlayer.position() - self.frameDurationMS)

    def initVideo(self):
        self.mediaPlayer.mediaStatusChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.stateChanged.connect(self.stateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        self.videoSlider.sliderMoved.connect(self.setPosition)

    def playVideo(self):
        if self.stackedWidget.currentWidget() == self.labelImageWidget:
            # display the video Widget if currently the label image is displayed
            self.stackedWidget.setCurrentWidget(self.videoWidget)

        if self.mediaPlayer.state() == QMediaPlayer.StoppedState:
            # This is the init Video
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

    def positionChanged(self, position):
        self.videoSlider.setValue(position)
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            if position > self._end or position < self._begin:
                self.setPosition(self._begin)

    def durationChanged(self, duration):
        self.videoSlider.setRange(self._begin, self._end)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def setStartingPosition(self):
        self._begin = max(0.0, self.frame_to_ms(self.labelFrame) - self.videoRangeMS / 2.0)
        self._end = min(self._videoDuration, self.frame_to_ms(self.labelFrame) + self.videoRangeMS / 2.0)

    def setVideo(self):
        # TODO: move to init?
        self.mediaPlayer.setVideoOutput(self.videoWidget)
        video, self.labelFrame, self._videoDuration = self.database.get_video_from_image(self.labeled_images[self.image_idx])
        self.mediaPlayer.setMedia(
            QMediaContent(QUrl.fromLocalFile(str(self.basedir / video))))
        self.setStartingPosition()
        self.setPosition(self._begin)
        self.playButton.setEnabled(True)

    def getNotesFromUI(self):
        """Reads the text from a textbox and stores it in an SQL Database"""
        text = self.notesWidget.toPlainText()
        self.database.set_notes(self.labeled_images[self.image_idx], text)
        self.notesWidget.clear()

    def setNotesOfUI(self):
        """Retrieves Notes from SQL Database and updates the Notes Window"""
        note = self.database.get_notes(self.labeled_images[self.image_idx])
        self.notesWidget.setText(note)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

    def setSkipButtons(self, value: bool):
        self.prevFrameButton.setEnabled(value)
        self.nextFrameButton.setEnabled(value)

    def initButtons(self):
        self.nextImageButton.setEnabled(True)
        self.prevImageButton.setEnabled(True)
        self.playButton.setEnabled(True)

    def displayLabel(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        self.stackedWidget.setCurrentWidget(self.labelImageWidget)
        self.setSkipButtons(False)
        self.displayLabelButton.setEnabled(False)
        self.updateImages()

    def updateImages(self):
        self.image.setPixmap(QPixmap(str(self.basedir / self.labeled_images[self.image_idx])))
        # TODO: replace with calls to the SQL database rather than the files themselves
        path_to_labelled = self.basedir / 'labels/SegmentationClassVisualization'
        filename_labeled = pathlib.Path(self.labeled_images[self.image_idx]).stem + '.jpg'
        self.labelImage.setPixmap(QPixmap(str(path_to_labelled / filename_labeled)))

    @staticmethod
    def frame_to_ms(frame_number: int, fps: int = 25):
        return (frame_number/fps) * 1000.0
