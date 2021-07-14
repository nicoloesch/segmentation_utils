import os
import glob
import sys
from PyQt5.QtWidgets import QApplication
from ui.mainWindow import SegmentationUI
from ui.SegmentationAnalysisMain import SegAnalysisMain


def main():
    app = QApplication(sys.argv)
    window = SegAnalysisMain()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
