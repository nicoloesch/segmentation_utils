import sys
from PyQt5.QtWidgets import QApplication
from seg_utils.src.label_main import SegLabelMain
from seg_utils.src.selection_main import SegSelectionMain
import argparse


def main(args):

    app = QApplication(sys.argv)
    #window = SegSelectionMain() # this opens the selection window
    window = SegLabelMain()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    # Add arguments to argument parser
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main(args)
