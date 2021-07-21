from seg_utils.ui.selection import Ui_Form
from seg_utils.src import viewer_main, label_main
from PyQt5.QtWidgets import (QDialogButtonBox, QWidget)


class SegSelectionMain(QWidget, Ui_Form):
    def __init__(self):
        super(SegSelectionMain, self).__init__()
        self.setupUi(self)
        self.okButton = self.buttonBox.button(QDialogButtonBox.Ok)
        self.cancelButton = self.buttonBox.button(QDialogButtonBox.Cancel)
        self.okButton.clicked.connect(self.confirmation)
        self.cancelButton.clicked.connect(self.cancel)
        self.labeler = label_main.SegLabelMain()
        self.viewer = viewer_main.SegViewerMain()

    def confirmation(self):
        checked_button = self.optionButtons.checkedButton()
        if checked_button == self.labelingButton:
            self.close()
            self.labeler.show()
        elif checked_button == self.viewerButton:
            self.close()
            self.viewer.show()
        else:
            pass

    def cancel(self):
        self.close()
