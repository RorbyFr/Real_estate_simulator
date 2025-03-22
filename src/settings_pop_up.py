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

        # Button info keys
        self.BUTTON_INSTANCE = "button instance"
        self.BUTTON_FILE = "button file"
        self.BUTTON_PICTURE = "button picture"
        self.BUTTON_SYMBOL = "button symbol"

        # Language list of dictionary containing info buttons
        self.language_button_list = [
            {self.BUTTON_INSTANCE: self.english_translation_pushButton,
             self.BUTTON_FILE: "en.qm",
             self.BUTTON_PICTURE: "english.png"
             },
            {self.BUTTON_INSTANCE: self.french_translation_pushButton,
             self.BUTTON_FILE: "fr.qm",
             self.BUTTON_PICTURE: "french.png"
             },
        ]
        # Money list of dictionary containing info buttons
        self.money_button_list = [
            {self.BUTTON_INSTANCE: self.euro_pushButton,
             self.BUTTON_SYMBOL: "€",
             self.BUTTON_PICTURE: "euro_money.png"
             },
            {self.BUTTON_INSTANCE: self.pound_pushButton,
             self.BUTTON_SYMBOL: "£",
             self.BUTTON_PICTURE: "pound_money.png"
             },
            {self.BUTTON_INSTANCE: self.dollar_pushButton,
             self.BUTTON_SYMBOL: "$",
             self.BUTTON_PICTURE: "dollar_money.png"
             },
            {self.BUTTON_INSTANCE: self.yen_pushButton,
             self.BUTTON_SYMBOL: "¥",
             self.BUTTON_PICTURE: "yen_money.png"
             },
            {self.BUTTON_INSTANCE: self.rupee_pushButton,
             self.BUTTON_SYMBOL: "₹",
             self.BUTTON_PICTURE: "rupee_money.png"
             },
            {self.BUTTON_INSTANCE: self.ruble_pushButton,
             self.BUTTON_SYMBOL: "₽",
             self.BUTTON_PICTURE: "ruble_money.png"
             },
        ]

        # Load translation image
        for dict_language in self.language_button_list:
            common.load_scaled_icon_on_widget(dict_language[self.BUTTON_INSTANCE],
                                              os.path.join(common.RESOURCES_PATH, dict_language[self.BUTTON_PICTURE]),
                                              text_under=False, border_width=4, border_height=4)

        # Load money image
        margin_border = 10
        for dict_money in self.money_button_list:
            common.load_scaled_icon_on_widget(dict_money[self.BUTTON_INSTANCE],
                                              os.path.join(common.RESOURCES_PATH, dict_money[self.BUTTON_PICTURE]),
                                              text_under=False, border_width=margin_border, border_height=margin_border)

        # Apply specific style on button
        self.apply_style_button()

        # Connect button
        self.connect_all_button()

        # Initial French language
        self.current_language = None

        # Initial french button clicked
        self.last_language_button = self.french_translation_pushButton

        # Initial euro button clicked
        self.last_money_button = self.euro_pushButton

    def apply_style_button(self):
        """Use flat style and PointingHandCursor"""
        for dict_language in self.language_button_list:
            dict_language[self.BUTTON_INSTANCE].setFlat(True)
            dict_language[self.BUTTON_INSTANCE].setCursor(Qt.PointingHandCursor)
        for dict_money in self.money_button_list:
            dict_money[self.BUTTON_INSTANCE].setFlat(True)
            dict_money[self.BUTTON_INSTANCE].setCursor(Qt.PointingHandCursor)

    def connect_all_button(self):
        # Connect translation pushButton
        for dict_language in self.language_button_list:
            dict_language[self.BUTTON_INSTANCE].clicked.connect(lambda translate, qm=dict_language[self.BUTTON_FILE]:
                                                                self.launch_translate(qm))

        # Connect money pushButton
        for dict_money in self.money_button_list:
            dict_money[self.BUTTON_INSTANCE].clicked.connect(lambda change_money, money=dict_money[self.BUTTON_SYMBOL]:
                                                             self.change_money(money))

        # Connect pop up closure to ok button
        self.ok_pushButton.clicked.connect(self.close_pop_up)

    def get_button_from_element(self, key, key_value):
        """ Get the button instance from key

        :params key: string key in (self.BUTTON_FILE, self.BUTTON_PICTURE, self.BUTTON_SYMBOL)
        :params key_value: string value corresponding to key
        :return: QPushButton instance button
        """

        for button_list in [self.language_button_list, self.money_button_list]:
            # Verify if key exist in list of dict
            if key not in button_list[0].keys():
                continue
            # Search for dict with tuple (key, key_value)
            for target_dict in button_list:
                if (key, key_value) in target_dict.items():
                    return target_dict[self.BUTTON_INSTANCE]

    def update_clicked_button(self, button, language_button):
        """Non-enable clicked button and enable last button clicked

        :params button: QPushButton button
        :params language_button: boolean to update language or money button
        :return: None
        """
        # Enabled old button
        last_button = self.last_language_button if language_button else self.last_money_button
        last_button.setEnabled(True)

        # Non-enable clicked button
        button.setEnabled(False)

        # Update last button clicked
        if language_button:
            self.last_language_button = button
        else:
            self.last_money_button = button

    @Slot(str)
    def change_money(self, money):
        # Update current money button, don't use sender() because change_money can be call without button clicking
        button = self.get_button_from_element(self.BUTTON_SYMBOL, money)
        self.update_clicked_button(button, False)
        # Change global money variable and retranslate
        common.MONEY_UNIT = money
        self.launch_translate(self.current_language)

    @Slot(str)
    def launch_translate(self, text):
        # Update current language button, don't use sender() because change_money can be call without button clicking
        button = self.get_button_from_element(self.BUTTON_FILE, text)
        self.update_clicked_button(button, True)
        # Retranslate text
        self.current_language = text
        self.sig_translate.emit(text)

    @Slot()
    def close_pop_up(self):
        self.hide()

    @Slot()
    def display_pop_up(self):
        self.show()
