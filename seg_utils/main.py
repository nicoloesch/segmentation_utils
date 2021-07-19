import sys
from PyQt5.QtWidgets import QApplication
from seg_utils.src.segLabelMain import SegLabelMain
from seg_utils.src.segSelectionMain import SegSelectionMain


def main():
    app = QApplication(sys.argv)
    #window = SegSelectionMain() # this opens the selection window
    window = SegLabelMain()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
