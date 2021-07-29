# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'viewer.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5 import QtCore, QtWidgets
from seg_utils.ui.image_viewer import ImageViewer
from seg_utils.utils.qt import getIcon


class ViewerUI(object):
    def setupUi(self, MainWindow):

        # -----------
        # MAIN WINDOW
        # -----------
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1567, 929)
        self.mainWidget = QtWidgets.QWidget(MainWindow)
        self.mainWidget.setObjectName("mainWidget")
        self.mainLayout = QtWidgets.QVBoxLayout(self.mainWidget)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setObjectName("mainLayout")

        # -----------
        # MAIN BODY - Body of the Main Window
        # -----------
        self.mainBody = QtWidgets.QFrame(self.mainWidget)
        self.mainBody.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.mainBody.setFrameShadow(QtWidgets.QFrame.Raised)
        self.mainBody.setObjectName("mainBody")
        self.bodyLayout = QtWidgets.QVBoxLayout(self.mainBody)
        self.bodyLayout.setContentsMargins(0, 0, 0, 0)
        self.bodyLayout.setSpacing(0)
        self.bodyLayout.setObjectName("bodyLayout")

        # -----------
        # ImageFrame - Frame containing left and right image
        # -----------
        self.imageFrame = QtWidgets.QFrame(self.mainBody)
        self.imageFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.imageFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.imageFrame.setObjectName("imageFrame")
        self.imageFrame.setMinimumWidth(800)
        self.imageFrame.setMaximumWidth(1800)
        self.imageLayout = QtWidgets.QHBoxLayout(self.imageFrame)
        self.imageLayout.setContentsMargins(0, 0, 0, 0)
        self.imageLayout.setSpacing(0)
        self.imageLayout.setObjectName("imageLayout")

        # Raw Image Viewer which is part of Image Frame
        self.rawImage = ImageViewer(self.imageFrame)
        self.rawImage.setObjectName("rawImage")
        self.rawImage.setMinimumWidth(400)
        self.rawImage.setMaximumWidth(900)
        self.imageLayout.addWidget(self.rawImage)

        # Right Image as Stacked Widget to switch between Video and Display labeling
        self.stackedWidget = QtWidgets.QStackedWidget(self.imageFrame)
        self.stackedWidget.setMinimumWidth(400)
        self.stackedWidget.setMaximumWidth(800)
        self.stackedWidget.setObjectName("stackedWidget")

        self.labelImage = ImageViewer(self.stackedWidget)
        self.labelImage.setMinimumWidth(400)
        self.labelImage.setMaximumWidth(900)
        self.labelImage.setObjectName("labelImage")
        self.stackedWidget.addWidget(self.labelImage)

        self.videoWidget = QVideoWidget(self.stackedWidget)
        self.videoWidget.setMinimumWidth(400)
        self.videoWidget.setMaximumWidth(800)
        self.videoWidget.setObjectName("videoWidget")
        self.stackedWidget.addWidget(self.videoWidget)
        self.stackedWidget.setCurrentIndex(0)

        self.imageLayout.addWidget(self.stackedWidget)
        self.imageLayout.setStretch(0, 1)
        self.imageLayout.setStretch(1, 1)
        self.bodyLayout.addWidget(self.imageFrame)

        # Control Frame below the images with sizes of max and min the width of the images and 50 height
        self.controlFrame = QtWidgets.QFrame(self.mainBody)
        self.controlFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.controlFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.controlFrame.setObjectName("controlFrame")
        self.controlFrame.setMinimumWidth(800)
        self.controlFrame.setMaximumWidth(1800)
        self.controlFrame.setMaximumHeight(50)
        self.controlFrame.setMinimumHeight(50)
        self.controlLayout = QtWidgets.QHBoxLayout(self.controlFrame)
        self.controlLayout.setContentsMargins(0, 0, 0, 0)
        self.controlLayout.setSpacing(0)
        self.controlLayout.setObjectName("controlFrame")

        self.imageControlFrame = QtWidgets.QFrame(self.controlFrame)
        self.imageControlFrame.setMaximumSize(QtCore.QSize(900, 50))
        self.imageControlFrame.setMinimumSize(QtCore.QSize(400, 50))
        self.imageControlFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.imageControlFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.imageControlFrame.setObjectName("imageControlFrame")
        self.imageControlLayout = QtWidgets.QHBoxLayout(self.imageControlFrame)
        self.imageControlLayout.setContentsMargins(0, 0, 0, 0)
        self.imageControlLayout.setSpacing(0)
        self.imageControlLayout.setObjectName("imageControlLayout")
        self.openDatabaseButton = QtWidgets.QPushButton(self.imageControlFrame)
        self.openDatabaseButton.setMinimumHeight(50)
        self.openDatabaseButton.setMaximumHeight(50)
        self.openDatabaseButton.setEnabled(True)
        self.openDatabaseButton.setText("Open Database")
        self.openDatabaseButton.setIcon(getIcon("open"))
        self.openDatabaseButton.setObjectName("openDatabaseButton")
        self.imageControlLayout.addWidget(self.openDatabaseButton)
        self.prevImageButton = QtWidgets.QPushButton(self.imageControlFrame)
        self.prevImageButton.setMinimumHeight(50)
        self.prevImageButton.setMaximumHeight(50)
        self.prevImageButton.setEnabled(False)
        self.prevImageButton.setText("Previous Image")
        self.prevImageButton.setIcon(getIcon("prev"))
        self.prevImageButton.setObjectName("prevImageButton")
        self.imageControlLayout.addWidget(self.prevImageButton)
        self.nextImageButton = QtWidgets.QPushButton(self.imageControlFrame)
        self.nextImageButton.setMinimumHeight(50)
        self.nextImageButton.setMaximumHeight(50)
        self.nextImageButton.setEnabled(False)
        self.nextImageButton.setText("Next Image")
        self.nextImageButton.setIcon(getIcon("next"))
        self.nextImageButton.setObjectName("nextImageButton")
        self.imageControlLayout.addWidget(self.nextImageButton)
        self.controlLayout.addWidget(self.imageControlFrame)

        # Add controls to the video
        self.videoControlFrame = QtWidgets.QFrame(self.controlFrame)
        self.videoControlFrame.setMaximumSize(QtCore.QSize(900, 50))
        self.videoControlFrame.setMinimumSize(QtCore.QSize(400, 50))
        self.videoControlFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.videoControlFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.videoControlFrame.setObjectName("videoControlFrame")
        self.videoControlLayout = QtWidgets.QVBoxLayout(self.videoControlFrame)
        self.videoControlLayout.setContentsMargins(0, 0, 0, 0)
        self.videoControlLayout.setSpacing(0)
        self.videoControlLayout.setObjectName("videoControlLayout")

        # Frame for slider within the video controls
        self.sliderFrame = QtWidgets.QFrame(self.videoControlFrame)
        self.sliderFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.sliderFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.sliderFrame.setObjectName("sliderFrame")
        self.sliderLayout = QtWidgets.QHBoxLayout(self.sliderFrame)
        self.sliderLayout.setContentsMargins(0, 0, 0, 0)
        self.sliderLayout.setSpacing(0)
        self.sliderLayout.setObjectName("sliderLayout")
        self.videoSlider = QtWidgets.QSlider(self.sliderFrame)
        self.videoSlider.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.videoSlider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.videoSlider.setObjectName("videoSlider")
        self.sliderLayout.addWidget(self.videoSlider)
        self.videoControlLayout.addWidget(self.sliderFrame)
        
        self.videoControlButtonsFrame = QtWidgets.QFrame(self.videoControlFrame)
        self.videoControlButtonsFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.videoControlButtonsFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.videoControlButtonsFrame.setObjectName("videoControlButtonsFrame")
        self.videoControlButtonsLayout = QtWidgets.QHBoxLayout(self.videoControlButtonsFrame)
        self.videoControlButtonsLayout.setContentsMargins(0, 0, 0, 0)
        self.videoControlButtonsLayout.setSpacing(0)
        self.videoControlButtonsLayout.setObjectName("videoControlButtonsLayout")
        self.playButton = QtWidgets.QPushButton(self.videoControlButtonsFrame)
        self.playButton.setEnabled(False)
        self.playButton.setText("")
        self.playButton.setIcon(getIcon("play"))
        self.playButton.setObjectName("playButton")
        self.videoControlButtonsLayout.addWidget(self.playButton)
        self.prevFrameButton = QtWidgets.QPushButton(self.videoControlButtonsFrame)
        self.prevFrameButton.setEnabled(False)
        self.prevFrameButton.setText("")
        self.prevFrameButton.setIcon(getIcon("rewind"))
        self.prevFrameButton.setObjectName("prevFrameButton")
        self.videoControlButtonsLayout.addWidget(self.prevFrameButton)
        self.nextFrameButton = QtWidgets.QPushButton(self.videoControlButtonsFrame)
        self.nextFrameButton.setEnabled(False)
        self.nextFrameButton.setText("")
        self.nextFrameButton.setIcon(getIcon("fast-forward"))
        self.nextFrameButton.setObjectName("nextFrameButton")
        self.videoControlButtonsLayout.addWidget(self.nextFrameButton)
        self.displayLabelButton = QtWidgets.QPushButton(self.videoControlButtonsFrame)
        self.displayLabelButton.setEnabled(False)
        self.displayLabelButton.setIcon(getIcon("image"))
        self.displayLabelButton.setObjectName("displayLabelButton")
        self.videoControlButtonsLayout.addWidget(self.displayLabelButton)

        self.videoControlLayout.addWidget(self.videoControlButtonsFrame)
        self.controlLayout.addWidget(self.videoControlFrame)
        self.controlLayout.setStretch(0, 1)
        self.controlLayout.setStretch(1, 1)
        self.bodyLayout.addWidget(self.controlFrame)

        self.notesWidget = QtWidgets.QTextEdit(self.mainBody)
        self.notesWidget.setMaximumSize(1800, 100)
        self.notesWidget.setPlaceholderText("Insert Notes here")
        self.notesWidget.setObjectName("notesWidget")

        self.bodyLayout.addWidget(self.notesWidget)
        self.mainLayout.addWidget(self.mainBody)

        # Add Menu and statusbar
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1567, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        MainWindow.setCentralWidget(self.mainWidget)




