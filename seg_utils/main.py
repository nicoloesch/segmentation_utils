import sys
from PyQt5.QtWidgets import QApplication
from seg_utils.ui.segViewerMain import SegViewerMain
from seg_utils.ui.segSelectionMain import SegSelectionMain


def main():
    app = QApplication(sys.argv)
    window = SegSelectionMain()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
