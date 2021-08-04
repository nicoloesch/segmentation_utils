import sys

from PyQt5.QtWidgets import QApplication
from seg_utils.src.label_main import LabelMain
from seg_utils.src.selection_main import SelectionMain
from seg_utils.src.viewer_main import ViewerMain
import argparse


import numpy as np
from PyQt5.QtGui import QPolygonF
from PyQt5.QtCore import QPointF


def main(args):

    app = QApplication(sys.argv)
    #window = SegSelectionMain()  # this opens the selection window
    window = LabelMain()
    #window = SegViewerMain()
    window.show()
    sys.exit(app.exec_())


def closest_node(node, nodes):
    dist_2 = np.sum((nodes - node)**2, axis=1)
    return np.argmin(dist_2)


def test():
    r"""Function for testing stuff"""
    vertices = np.array([[0, 0],
                         [1, 0],
                         [1, 1],
                         [0, 1]])
    testPoint = np.array([1.0, 0])

    a = closest_node(testPoint, vertices)
    four = 4

if __name__ == "__main__":
    test()
    # Add arguments to argument parser
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    main(args)
