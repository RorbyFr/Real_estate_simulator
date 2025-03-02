
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCore import QSize, Qt, QTranslator, QLocale, Slot, QEvent
from PySide6.QtGui import QIcon, QFont

from resources.main_window import Ui_MainWindow
from settings_pop_up import SettingsPopUp
from real_estate_page import YearFinderPage, HouseSizeFinderPage, ContributionFinderPage, MonthlyPaymentFinderPage, InterestRateFinderPage
import common

import os
import sys


class MainWindow(QMainWindow, Ui_MainWindow):

    # Key in buttons dictionary
    IMG_KEY = "image path"
    IDX_KEY = "index page"

    def __init__(self):
        super(MainWindow, self).__init__()
        # Apply UI file
        self.setupUi(self)

        # Translator to switch language
        self.translator = QTranslator()

        # Remove up windows bar
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.home_buttons = {
            self.year_toolButton: {self.IMG_KEY: "year.png", self.IDX_KEY: 1},
            self.house_size_toolButton: {self.IMG_KEY: "house size.PNG", self.IDX_KEY: 2},
            self.contribution_toolButton: {self.IMG_KEY: "contribution.PNG", self.IDX_KEY: 3},
            self.monthly_payment_toolButton: {self.IMG_KEY: "monthly payment.PNG", self.IDX_KEY: 4},
            self.interest_rate_toolButton: {self.IMG_KEY: "interest rate.PNG", self.IDX_KEY: 5},
        }

        # Back to main page button
        common.load_scaled_icon_on_widget(self.back_pushButton, os.path.join(common.RESOURCES_PATH, "back.png"), text_under=False)
        self.back_pushButton.clicked.connect(lambda checked, index=0: self.go_to_page(index))
        # Qt bug need define here cursor instead of css
        self.back_pushButton.setCursor(Qt.PointingHandCursor)

        # Settings button
        common.load_scaled_icon_on_widget(self.settings_pushButton, os.path.join(common.RESOURCES_PATH, "settings.png"), text_under=False)
        self.settings_pushButton.clicked.connect(self.open_settings)
        self.settings_pushButton.setCursor(Qt.PointingHandCursor)

        # Quit button
        common.load_scaled_icon_on_widget(self.quit_pushButton, os.path.join(common.RESOURCES_PATH, "red_cross.png"), text_under=False)
        self.quit_pushButton.clicked.connect(self.quit_application)
        self.quit_pushButton.setCursor(Qt.PointingHandCursor)

        self.__create_home_buttons()

        # Apply stylesheet
        stylesheet_path = os.path.join(common.RESOURCES_PATH, "stylesheet.css")
        common.apply_stylesheet(self, stylesheet_path)

        # Innit settings pop up
        self.settings_pop_up = SettingsPopUp()

        self.settings_pop_up.sig_translate.connect(self.change_language)

        # Year page (idx 1)
        self.year_finder_page = YearFinderPage()
        self.stackedWidget.addWidget(self.year_finder_page)
        # House size page (idx 2)
        self.house_size_finder_page = HouseSizeFinderPage()
        self.stackedWidget.addWidget(self.house_size_finder_page)
        # Contribution page (idx 3)
        self.contribution_finder_page = ContributionFinderPage()
        self.stackedWidget.addWidget(self.contribution_finder_page)
        # Monthly payment page (idx 4)
        self.monthly_payment_finder_page = MonthlyPaymentFinderPage()
        self.stackedWidget.addWidget(self.monthly_payment_finder_page)
        # Monthly payment page (idx 5)
        self.interest_rate_finder_page = InterestRateFinderPage()
        self.stackedWidget.addWidget(self.interest_rate_finder_page)

        # Store main menu title before go to page
        self.main_menu_title = self.title.text()
        # Start on home page
        self.current_index = 0
        self.go_to_page(self.current_index)

        # Init display app in french and euro
        self.settings_pop_up.launch_translate("fr.qm")
        self.settings_pop_up.change_money("€")

    def __create_home_buttons(self):
        """Put icon on home buttons"""
        for button, data_button in self.home_buttons.items():
            # Put icon on button with text under
            common.load_scaled_icon_on_widget(button, os.path.join(common.RESOURCES_PATH, data_button[self.IMG_KEY]), text_under=True)
            button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            # Connect changing page
            button.clicked.connect(lambda checked, index=data_button[self.IDX_KEY]: self.go_to_page(index))
            # Qt bug need define here cursor instead of css
            button.setCursor(Qt.PointingHandCursor)

    def load_scaled_icon_on_button(self, widget, img_path, text_under=True):
        """ Load image and resize it to fit with widget

        :params widget: QWidget
        :params img_path: string path of image
        :params text_under: boolean to put text under button
        """
        icon = QIcon(img_path)
        widget_width = widget.size().width()
        widget_height = widget.size().height()
        coefficient_under = 1
        if text_under:
            coefficient_under = 0.70
        width, height = self.find_optimal_icon_size(widget_width, int(widget_height*coefficient_under), icon)
        widget.setIcon(icon)
        widget.setIconSize(QSize(width, height))

    @staticmethod
    def find_optimal_icon_size(target_width, target_height, icon):
        """Find optimal dimension to fit icon on widget

        :params target_width: int target width
        :params target_height: int target height
        :params icon: QIcon
        """
        width = icon.availableSizes()[0].width()
        height = icon.availableSizes()[0].height()

        # Calcul ratio
        width_ratio = target_width/width
        height_ratio = target_height/height

        # Take minimum ratio to fit with at least on one dimension and not cross edge widget
        new_ratio = min(width_ratio, height_ratio)
        new_width = int(width * new_ratio)
        new_height = int(height * new_ratio)

        return new_width, new_height

    def go_to_page(self, index):
        """Go on target page

        :params index: int index, 0 is main menu
        """
        self.stackedWidget.setCurrentIndex(index)
        if index == 0:
            self.back_pushButton.setVisible(False)
            self.title.setText(self.main_menu_title)
            font_size = 40
        else:
            self.back_pushButton.setVisible(True)
            # Display button name in title, real estate page title are smaller than main menu title
            current_button = list(self.home_buttons.items())[index - 1][0]
            self.title.setText(current_button.text())
            font_size = 30
        # Display text in Arial black
        font = QFont("Rockwell")
        font.setPointSize(font_size)
        self.title.setFont(font)
        # Save current index
        self.current_index = index
        # Give current page to sub page
        self.give_current_page_to_real_estate_page(index)

    def give_current_page_to_real_estate_page(self, index):
        list_page = [self, self.year_finder_page, self.house_size_finder_page, self.contribution_finder_page,
                     self.monthly_payment_finder_page, self.interest_rate_finder_page]
        for page in list_page:
            page.current_page = list_page[index]

    @Slot()
    def open_settings(self):
        """Open settings to choose language and money unity"""
        self.settings_pop_up.display_pop_up()

    @Slot(str)
    def change_language(self, lang):
        file_lang = os.path.join(common.RESOURCES_PATH, lang)
        if self.translator.load(file_lang):
            QApplication.instance().installTranslator(self.translator)
            # Translate first python file generated from UI
            for widget in QApplication.instance().allWidgets():
                if hasattr(widget, "retranslateUi"):
                    widget.retranslateUi(self)
            # Translate secondly manual setting text in code
            for widget in QApplication.instance().allWidgets():
                # print(widget)
                # print()
                if hasattr(widget, "retranslate_page"):
                    widget.retranslate_page()
                elif hasattr(widget, "retranslate_title"):
                    widget.retranslate_title()
                elif hasattr(widget, "retranslate_graphic"):
                    widget.retranslate_graphic()

    def retranslate_title(self):
        # Save main menu title translated with retranslateUi to use in go_to_page method
        self.main_menu_title = self.title.text()
        # Home page
        if self.current_index == 0:
            self.title.setText(self.main_menu_title)
        # Real estate page
        else:
            current_button = list(self.home_buttons.items())[self.current_index - 1][0]
            self.title.setText(current_button.text())

    @Slot()
    def quit_application(self):
        """Quit application when red cross button is pushed"""
        self.year_finder_page.simulator_thread.quit()
        self.house_size_finder_page.simulator_thread.quit()
        self.contribution_finder_page.simulator_thread.quit()
        self.monthly_payment_finder_page.simulator_thread.quit()
        self.interest_rate_finder_page.simulator_thread.quit()
        sys.exit()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    # translator = QTranslator()
    # locale = QLocale.system().name()  # Ex: "fr_FR"
    # qm_file_path = os.path.join(RESOURCES_PATH, f"{locale}.qm")
    # if translator.load(qm_file_path):
    #     app.installTranslator(translator)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
