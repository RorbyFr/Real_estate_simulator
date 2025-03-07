from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from math import ceil

from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Slot

import common


class MatplotlibWidget(QWidget):
    def __init__(self, title, xlabel, ylabel):
        """Initialize display statistic Widget

        :params title: string title of graphic
        :params xlabel: string label of X axis
        :params ylabel: string label of Y axis
        """
        super(MatplotlibWidget, self).__init__()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)
        self.init_plot(title, xlabel, ylabel)

        self.loan_line = None
        self.interest_line = None
        self.bar_loan = None
        self.bar_interest = None

        self.last_year = None
        self.last_loan_payment_cumulated = None
        self.last_interest_payment_cumulated = None
        self.last_loan_payment = None
        self.last_interest_payment = None

    def init_plot(self, title, xlabel, ylabel):
        """Initialize statistic display

        :params title: string title of graphic
        :params xlabel: string label of X axis
        :params ylabel: string label of Y axis
        """
        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.canvas.draw()


class LoanInterestCumulatedDisplay(MatplotlibWidget):
    def __init__(self):
        super().__init__(self.tr("Cumulated expense depending on years"), self.tr("Years"), self.tr("Cumulated expense (€)"))

    def display(self, year, loan_payment_cumulated, interest_payment_cumulated):
        """Display cumulated loan and cumulated interest

        :params year: list of int year
        :params loan_payment_cumulated: list of float cumulated loan payment
        :params interest_payment_cumulated: list of float cumulated interest payment
        """
        # Clean previous display
        if self.loan_line:
            self.loan_line.remove()
            self.interest_line.remove()
        year_list = [i for i in range(1, ceil(year) + 1)]
        loan_label = self.tr("cumulated loan")
        interest_label = self.tr("cumulated interest")
        # Keep reference of line to clean
        (self.loan_line,) = self.ax.plot(year_list, loan_payment_cumulated, label=loan_label, color="blue", marker="o")
        (self.interest_line,) = self.ax.plot(year_list, interest_payment_cumulated, label=interest_label, color="red", marker="o")
        self.ax.grid(True)
        self.figure.tight_layout()
        self.ax.get_legend().remove() if self.ax.get_legend() else None
        self.ax.legend([self.loan_line, self.interest_line], [loan_label, interest_label], loc="best")

        # Draw on canvas
        self.figure.canvas.draw()

        # Save parameters to retranslate later
        self.last_year = year
        self.last_loan_payment_cumulated = loan_payment_cumulated
        self.last_interest_payment_cumulated = interest_payment_cumulated

    def retranslate_graphic(self):
        title = self.tr("Cumulated expense depending on years")
        x = self.tr("Years")
        y = self.tr("Cumulated expense (€)").replace("€", common.MONEY_UNIT)
        self.init_plot(title, x, y)
        # Update legend if exist
        if self.last_year is not None:
            self.display(self.last_year, self.last_loan_payment_cumulated, self.last_interest_payment_cumulated)

    @Slot()
    def clean_graphic(self):
        if self.loan_line is not None:
            self.loan_line.remove()
            self.interest_line.remove()
            self.ax.get_legend().remove() if self.ax.get_legend() else None
            self.figure.canvas.draw()
            # Reinit variables
            self.last_year = None
            self.last_loan_payment_cumulated = None
            self.last_interest_payment_cumulated = None
            self.loan_line = None
            self.interest_line = None


class LoanInterestRatioDisplay(MatplotlibWidget):
    def __init__(self):
        super().__init__(self.tr("Loan/interest ratio depending on years"), self.tr("Years"), self.tr("Ratio (%)"))

    def display(self, year, loan_payment, interest_payment):
        """Display Loan and interest ratio

        :params year: list of int year
        :params loan_payment: list of float loan payment
        :params interest_payment: list of float interest payment
        """
        # Clean previous display
        if self.bar_loan:
            for bar in self.bar_loan:
                bar.remove()
            for bar in self.bar_interest:
                bar.remove()
        year_list = [i for i in range(1, ceil(year) + 1)]
        # Calcul ratio in percentage
        loan_ratio = [loan_payment[i] / (loan_payment[i] + interest_payment[i]) for i in range(len(loan_payment))]
        interest_ratio = [interest_payment[i] / (loan_payment[i] + interest_payment[i]) for i in range(len(interest_payment))]
        loan_label = self.tr("Loan")
        interest_label = self.tr("Interest")
        # Display loan/interest ratio
        self.bar_loan = self.ax.bar(year_list, loan_ratio, label=loan_label, color="skyblue")
        self.bar_interest = self.ax.bar(year_list, interest_ratio, bottom=loan_ratio, label=interest_label, color="lightcoral")
        self.ax.set_xticks(year_list)
        self.figure.tight_layout()
        self.ax.get_legend().remove() if self.ax.get_legend() else None
        self.ax.legend([self.bar_loan, self.bar_interest], [loan_label, interest_label], loc="best")
        # Draw on canvas
        self.figure.canvas.draw()

        # Save parameters to retranslate later
        self.last_year = year
        self.last_loan_payment = loan_payment
        self.last_interest_payment = interest_payment

    def retranslate_graphic(self):
        title = self.tr("Loan/interest ratio depending on years")
        x = self.tr("Years")
        y = self.tr("Ratio (%)")
        self.init_plot(title, x, y)
        # Update legend if exist
        if self.last_year is not None:
            self.display(self.last_year, self.last_loan_payment, self.last_interest_payment)

    @Slot()
    def clean_graphic(self):
        if self.bar_loan is not None:
            for bar in self.bar_loan:
                bar.remove()
            for bar in self.bar_interest:
                bar.remove()
            self.ax.get_legend().remove() if self.ax.get_legend() else None
            self.figure.canvas.draw()
            # Reinit variables
            self.last_year = None
            self.last_loan_payment = None
            self.last_interest_payment = None
            self.bar_loan = None
            self.bar_interest = None
