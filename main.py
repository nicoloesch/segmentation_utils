import os
import glob
import sys
from PyQt5.QtWidgets import QApplication
from ui.mainWindow import Ui_MainWindow


def main():
    app = QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
