from PySide6.QtCore import Slot, Qt

from resources.error_pop_up import Ui_Dialog
import common

import os


class ErrorPopUp(Ui_Dialog, common.RoundedQdialog):

    def __init__(self):
        Ui_Dialog.__init__(self)
        common.RoundedQdialog.__init__(self, radius=30, color=Qt.white, border_color=Qt.black, border_width=8)

        # Apply UI
        self.setupUi(self)

        # Apply stylesheet
        stylesheet_path = os.path.join(common.RESOURCES_PATH, "stylesheet_error_pop_up.css")
        common.apply_stylesheet(self, stylesheet_path)

        # Remove upside bar and keep pop-up and first view
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Load error image
        common.load_scaled_icon_on_widget(self.error_image, os.path.join(common.RESOURCES_PATH, "error.png"))
        # self.verticalLayout.setAlignment(Qt.AlignTop)
        self.error_image.setAlignment(Qt.AlignCenter)

        # Center text and button
        self.verticalLayout.setAlignment(Qt.AlignCenter)

        # Return to line if text is too long
        self.error_label.setWordWrap(True)

        # Connect pop up closure to ok button
        self.ok_pushButton.clicked.connect(self.close_pop_up)

    @Slot()
    def close_pop_up(self):
        self.error_label.setText("")
        self.hide()

    @Slot(str)
    def display_pop_up(self, message):
        self.error_label.setText(message)
        self.show()

