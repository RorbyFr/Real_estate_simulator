from PySide6.QtCore import Signal, Slot, Qt

from resources.settings_pop_up import Ui_Dialog
import common

import os


class SettingsPopUp(Ui_Dialog, common.RoundedQdialog):
    sig_translate = Signal(str)

    def __init__(self):
        Ui_Dialog.__init__(self)
        common.RoundedQdialog.__init__(self, radius=30, color=Qt.white, border_color=Qt.black, border_width=8)

        # Apply UI
        self.setupUi(self)

        # Apply stylesheet
        stylesheet_path = os.path.join(common.RESOURCES_PATH, "stylesheet_settings_pop_up.css")
        common.apply_stylesheet(self, stylesheet_path)

        # Remove upside bar and keep pop-up and first view
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Load translation image
        common.load_scaled_icon_on_widget(self.english_translation_pushButton,
                                          os.path.join(common.RESOURCES_PATH, "english.png"),
                                          text_under=False, border_width=4, border_height=4)
        common.load_scaled_icon_on_widget(self.french_translation_pushButton,
                                          os.path.join(common.RESOURCES_PATH, "french.png"),
                                          text_under=False, border_width=4, border_height=4)

        # Load money image
        margin_border = 10
        common.load_scaled_icon_on_widget(self.euro_pushButton, os.path.join(common.RESOURCES_PATH, "euro_money.png"),
                                          text_under=False, border_width=margin_border, border_height=margin_border)
        common.load_scaled_icon_on_widget(self.pound_pushButton, os.path.join(common.RESOURCES_PATH, "pound_money.png"),
                                          text_under=False, border_width=margin_border, border_height=margin_border)
        common.load_scaled_icon_on_widget(self.dollar_pushButton,
                                          os.path.join(common.RESOURCES_PATH, "dollar_money.png"),
                                          text_under=False, border_width=margin_border, border_height=margin_border)
        common.load_scaled_icon_on_widget(self.yen_pushButton, os.path.join(common.RESOURCES_PATH, "yen_money.png"),
                                          text_under=False, border_width=margin_border, border_height=margin_border)
        common.load_scaled_icon_on_widget(self.rupee_pushButton, os.path.join(common.RESOURCES_PATH, "rupee_money.png"),
                                          text_under=False, border_width=margin_border, border_height=margin_border)
        common.load_scaled_icon_on_widget(self.ruble_pushButton, os.path.join(common.RESOURCES_PATH, "ruble_money.png"),
                                          text_under=False, border_width=margin_border, border_height=margin_border)

        # Apply specific style on button
        self.apply_style_button()

        # Connect button
        self.connect_all_button()

        # Initial french language
        self.current_language = None

    def apply_style_button(self):
        # Flat button
        self.english_translation_pushButton.setFlat(True)
        self.french_translation_pushButton.setFlat(True)
        self.euro_pushButton.setFlat(True)
        self.pound_pushButton.setFlat(True)
        self.dollar_pushButton.setFlat(True)
        self.yen_pushButton.setFlat(True)
        self.rupee_pushButton.setFlat(True)
        self.ruble_pushButton.setFlat(True)
        # Pointer style
        self.english_translation_pushButton.setCursor(Qt.PointingHandCursor)
        self.french_translation_pushButton.setCursor(Qt.PointingHandCursor)
        self.euro_pushButton.setCursor(Qt.PointingHandCursor)
        self.pound_pushButton.setCursor(Qt.PointingHandCursor)
        self.dollar_pushButton.setCursor(Qt.PointingHandCursor)
        self.yen_pushButton.setCursor(Qt.PointingHandCursor)
        self.rupee_pushButton.setCursor(Qt.PointingHandCursor)
        self.ruble_pushButton.setCursor(Qt.PointingHandCursor)

    def connect_all_button(self):
        # Connect translation pushButton
        self.english_translation_pushButton.clicked.connect(lambda translate, qm="en.qm": self.launch_translate(qm))
        self.french_translation_pushButton.clicked.connect(lambda translate, qm="fr.qm": self.launch_translate(qm))

        # Connect money pushButton
        self.euro_pushButton.clicked.connect(lambda change_money, money="€": self.change_money(money))
        self.pound_pushButton.clicked.connect(lambda change_money, money="£": self.change_money(money))
        self.dollar_pushButton.clicked.connect(lambda change_money, money="$": self.change_money(money))
        self.yen_pushButton.clicked.connect(lambda change_money, money="¥": self.change_money(money))
        self.rupee_pushButton.clicked.connect(lambda change_money, money="₹": self.change_money(money))
        self.ruble_pushButton.clicked.connect(lambda change_money, money="₽": self.change_money(money))

        # Connect pop up closure to ok button
        self.ok_pushButton.clicked.connect(self.close_pop_up)

    @Slot(str)
    def change_money(self, money):
        common.MONEY_UNIT = money
        self.launch_translate(self.current_language)

    @Slot(str)
    def launch_translate(self, text):
        self.current_language = text
        self.sig_translate.emit(text)

    @Slot()
    def close_pop_up(self):
        self.hide()

    @Slot()
    def display_pop_up(self):
        self.show()
