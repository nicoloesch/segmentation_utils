Before this .ui can be used, it needs to be transformed into a .py file.
.ui files originate from QT Designer and provide and easier design of UI.
To convert the file, one needs pyuic5 and the following command with activated python environment which contains an installation of PyQT5 (or the bin folder of python in the Path Variable instead of activate python env)

pyuic5 -x SegmentationAnalysis.ui -o SegmentationAnalysis.py

If the .ui contains selfmade icons or icons from a non-standard library, one needs to "compil" the .qrc file with

pyrcc5 ResourceFile.qrc -o DesiredOutput.py


