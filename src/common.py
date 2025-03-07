from PySide6.QtCore import QFile, QTextStream, QSize, Qt
from PySide6.QtGui import QIcon, QPixmap, QPainterPath, QPainter, QPen
from PySide6.QtWidgets import QDialog

import sys
import os


def get_absolute_path_from_relative(relative_path):
    """Get absolute path from relative path

    :params css_file: string relative path from Home project
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)


RESOURCES_PATH = get_absolute_path_from_relative("resources")


# Current money unit used
MONEY_UNIT = "€"
# Dictionary to convert money from euro (updated on 23/02/2025)
DICT_MONEY_CONVERSION = {"€": 1.00, "£": 0.83, "$": 1.05, "¥": 156.07, "₹": 90.58, "₽": 93.10}


def set_money_unit(value):
    global MONEY_UNIT
    MONEY_UNIT = value


def apply_stylesheet(class_name, css_file):
    """Apply stylesheet on main window

    :params css_file: string css_file path
    """
    file = QFile(css_file)
    if file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(file)
        css = stream.readAll()
        class_name.setStyleSheet(css)


def load_scaled_icon_on_widget(widget, img_path, text_under=True, border_width=0, border_height=0):
    """Load image and resize it to fit with widget

    :params widget: QWidget
    :params img_path: string path of image
    :params text_under: boolean to put text under widget
    :params border: int size of border
    """
    if hasattr(widget, "setIcon"):
        icon = QIcon(img_path)
        widget_width = widget.size().width() - border_width
        widget_height = widget.size().height() - border_height
        coefficient_under = 1
        if text_under:
            coefficient_under = 0.70
        width, height = find_optimal_icon_size(widget_width, int(widget_height * coefficient_under), icon)
        widget.setIcon(icon)
        widget.setIconSize(QSize(width, height))
    elif hasattr(widget, "setPixmap"):
        pixmap = QPixmap(img_path)
        widget_width = widget.width() - border_width
        widget_height = widget.height() - border_height
        coefficient_under = 1
        if text_under:
            coefficient_under = 0.70
        resized_pixmap = pixmap.scaled(widget_width, int(widget_height * coefficient_under), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        widget.setPixmap(resized_pixmap)


def find_optimal_icon_size(target_width, target_height, widget):
    """Find optimal dimension to fit icon on widget

    :params target_width: int target width
    :params target_height: int target height
    :params icon: widget as QIcon or QPixmap
    """
    if isinstance(widget, QIcon):
        width = widget.availableSizes()[0].width()
        height = widget.availableSizes()[0].height()
    elif isinstance(widget, QPixmap):
        width = widget.width()
        height = widget.height()

    # Calcul ratio
    width_ratio = target_width / width
    height_ratio = target_height / height

    # Take minimum ratio to fit with at least on one dimension and not cross edge widget
    new_ratio = min(width_ratio, height_ratio)
    new_width = int(width * new_ratio)
    new_height = int(height * new_ratio)

    return new_width, new_height


class _RoundedWidget(object):
    """Protected rounded widget class, this should be use as parent class of QWidget class
    (QWidget, QDialog, QMainWindow, ...)"""

    def __init__(self, radius, color, border_color, border_width):
        self.radius = radius
        self.color = color
        self.border_color = border_color
        self.border_width = border_width

        # Set translucent background to delete corners
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def paintEvent(self, event):
        """Paint event for Qwidget class which draw rounded window

        :param event: QEvent
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(self.border_color)
        pen.setWidth(self.border_width)

        painter.setPen(pen)

        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.radius, self.radius)

        painter.setBrush(self.color)

        painter.drawPath(path)


class RoundedQdialog(_RoundedWidget, QDialog):
    def __init__(self, radius, color, border_color, border_width):
        QDialog.__init__(self)
        _RoundedWidget.__init__(self, radius, color, border_color, border_width)
