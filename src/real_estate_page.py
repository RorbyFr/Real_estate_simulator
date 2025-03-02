from PySide6.QtCore import QThread, Slot, QCoreApplication
from PySide6.QtWidgets import QWidget, QLineEdit, QComboBox, QApplication

from resources.real_estate_finder import Ui_Form
from simulator_interface import SimulatorInterface
from error_pop_up import ErrorPopUp
from display_statistics import LoanInterestRatioDisplay, LoanInterestCumulatedDisplay
import common

import os
from functools import wraps


class RealEstatePage(QWidget, Ui_Form):

    def __init__(self, input_label_1, input_label_2, input_label_3, input_label_4, input_label_5,
                 calcul_button, output_label, widget_name):
        super(RealEstatePage, self).__init__()

        # Current page of gui
        self.current_page = None

        # Memory to know if outputs contains result to translate again application
        self.output_result, self.output_cumulated_loan, self.output_cumulated_interest = None, None, None

        # Text display in output label
        self.output_text = ""

        # Apply UI file
        self.setupUi(self)

        # Apply stylesheet
        stylesheet_path = os.path.join(common.RESOURCES_PATH, "stylesheet_pages.css")
        common.apply_stylesheet(self, stylesheet_path)

        # Update input label
        self.label_input_1.setText(input_label_1)
        self.label_input_2.setText(input_label_2)
        self.label_input_3.setText(input_label_3)
        self.label_input_4.setText(input_label_4)
        self.label_input_5.setText(input_label_5)
        self.label_combo_box.setText(QCoreApplication.translate("Real estate page", "Notary rate interest:"))
        # Update Calcul button
        self.simulation_pushButton.setText(calcul_button)
        # Update output label
        self.label_output.setText(output_label)
        # Set widget name
        self.setObjectName(widget_name)
        # Create display statistic widget
        self.loan_interest_cumulated = LoanInterestCumulatedDisplay()
        self.statistics_tabWidget.addTab(self.loan_interest_cumulated,
                                         QCoreApplication.translate("Graphic", "Cumulated loan and interest"))
        self.loan_interest_ratio = LoanInterestRatioDisplay()
        self.statistics_tabWidget.addTab(self.loan_interest_ratio,
                                         QCoreApplication.translate("Graphic", "Loan and interest ratio"))

        # Innit error pop up
        self.error_pop_up = ErrorPopUp()

        # Init simulation
        self.simulator = SimulatorInterface()

        self.simulator_thread = QThread()
        self.simulator.moveToThread(self.simulator_thread)
        self.simulator_thread.started.connect(self.simulator.connect_all_signal())
        self.simulator_thread.start()

        # Connect here update result label
        self.simulator.sig_get_result_simulation.connect(self._update_output_text)
        self.simulator.sig_display_result_statistic.connect(self._display_statistics)

        # Connect here simulation button
        self.simulation_pushButton.clicked.connect(self.launch_simulation)

        # Connect simulation parameter error, display pop-up reinit outputs label and clean graphic
        self.simulator.sig_parameter_error.connect(self.error_pop_up.display_pop_up)
        self.simulator.sig_parameter_error.connect(self.reinit_output)
        self.simulator.sig_parameter_error.connect(self.loan_interest_cumulated.clean_graphic)
        self.simulator.sig_parameter_error.connect(self.loan_interest_ratio.clean_graphic)

        # Connect next focus on QLineEdits
        self.lineEdit_input_1.returnPressed.connect(self.__give_focus_to_next_input)
        self.lineEdit_input_2.returnPressed.connect(self.__give_focus_to_next_input)
        self.lineEdit_input_3.returnPressed.connect(self.__give_focus_to_next_input)
        self.lineEdit_input_4.returnPressed.connect(self.__give_focus_to_next_input)

    def retranslate(self, input_label_1, input_label_2, input_label_3, input_label_4, input_label_5,
                    calcul_button, output_label):
        # Input line edit
        self.label_input_1.setText(input_label_1)
        self.label_input_2.setText(input_label_2)
        self.label_input_3.setText(input_label_3)
        self.label_input_4.setText(input_label_4)
        self.label_input_5.setText(input_label_5)
        # Notary interest combo box
        self.label_combo_box.setText(QCoreApplication.translate("Real estate page", "Notary rate interest:"))
        # Calcul button
        self.simulation_pushButton.setText(calcul_button)
        # Cumulated loan
        if self.output_cumulated_loan is not None:
            self.label_cumulated_loan.setText(QCoreApplication.translate("Real estate page", "Loan = {} €")
                                              .format(self.output_cumulated_loan)
                                              .replace("€", common.MONEY_UNIT))
        # Cumulated interest
        if self.output_cumulated_interest is not None:
            self.label_cumulated_interest.setText(QCoreApplication.translate("Real estate page", "Cumulated interest = {} €")
                                                  .format(self.output_cumulated_interest)
                                                  .replace("€", common.MONEY_UNIT))
        # Result in output label
        if self.output_result is not None:
            self.label_output.setText(self.output_text.format(result=self.output_result))
        # No result in output label
        else:
            self.label_output.setText(output_label)

        # Retranslate only once error pop-up
        if self.current_page == self:
            # Error pop-up
            error = self.simulator.get_translated_error()
            self.error_pop_up.error_label.setText(error)

        # Update tabwidget graphic names
        self.statistics_tabWidget.setTabText(0, QCoreApplication.translate("Graphic", "Cumulated loan and interest"))
        self.statistics_tabWidget.setTabText(1, QCoreApplication.translate("Graphic", "Loan and interest ratio"))

        # Update simulators models
        self.simulator.sig_refresh_model.emit()

    @staticmethod
    def launch_simulation_security(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            try:
                function(self, *args, **kwargs)
            except Exception:
                self.simulator.sig_last_error_changed.emit(self.simulator.INPUT_ERROR)
                self.simulator.sig_parameter_error.emit(
                    QCoreApplication.translate("Error pop-up", "Error in input parameter detected, please check your values"))
        return wrapper

    @Slot()
    @launch_simulation_security
    def launch_simulation(self):
        pass

    @Slot(str)
    def _update_output_text(self, text):
        self.label_output.setText(self.output_text.format(result=text))
        self.output_result = text

    @Slot(float, list, list, list, list)
    def _display_statistics(self, year, loan_payment, interest_payment,
                            cumulated_loan_payment, cumulated_interest_payment):
        # Update statistics graphics
        self.loan_interest_cumulated.display(year, cumulated_loan_payment, cumulated_interest_payment)
        self.loan_interest_ratio.display(year, loan_payment, interest_payment)
        # Update memory
        self.output_cumulated_loan = round(cumulated_loan_payment[-1], 2)
        self.output_cumulated_interest = round(cumulated_interest_payment[-1], 2)
        # Update loan and cumulated interest label
        self.label_cumulated_loan.setText(
            QCoreApplication.translate("Real estate page", "Loan = {} €").format(self.output_cumulated_loan)
            .replace("€", common.MONEY_UNIT))
        self.label_cumulated_interest.setText(
            QCoreApplication.translate("Real estate page", "Cumulated interest = {} €").format(self.output_cumulated_interest)
            .replace("€", common.MONEY_UNIT))

    def __get_rate_notary(self):
        # Old house
        if self.notary_rate_comboBox.currentIndex() == 0:
            return 0.08
        # New house
        else:
            return 0.03

    def _get_value_input(self, widget):
        """Get the current value of input widget
        :params widget: QWidget inherited instance
        """
        if isinstance(widget, QLineEdit):
            return float(widget.text())
        elif isinstance(widget, QComboBox):
            return self.__get_rate_notary()
        return None

    @Slot()
    def __give_focus_to_next_input(self):
        """ Give focus to next QLineEdit when Enter key is pressed"""
        focused_widget = QApplication.focusWidget()
        current_input = focused_widget.objectName()
        next_input = current_input[:-1] + str(int(current_input[-1]) + 1)
        self.findChild(QLineEdit, next_input).setFocus()

    @Slot()
    def reinit_output(self):
        # Set text
        self.label_cumulated_interest.setText(QCoreApplication.translate("Form", "Cumulated interest ="))
        self.label_cumulated_loan.setText(QCoreApplication.translate("Form", "Loan ="))
        output_result = self.get_init_output_label()
        self.label_output.setText(output_result)
        # Reinit output variable to retranslate with None result
        self.output_cumulated_loan = None
        self.output_cumulated_interest = None
        self.output_result = None


class YearFinderPage(RealEstatePage):

    def __init__(self):
        super(YearFinderPage, self).__init__(input_label_1=QCoreApplication.translate("Real estate page", "House size (m²)"),
                                             input_label_2=QCoreApplication.translate("Real estate page", "Surface rate price (€/m²)"),
                                             input_label_3=QCoreApplication.translate("Real estate page", "Contribution (€)"),
                                             input_label_4=QCoreApplication.translate("Real estate page", "Monthly payment (€/month)"),
                                             input_label_5=QCoreApplication.translate("Real estate page", "Interest rate (%)"),
                                             calcul_button=QCoreApplication.translate("Real estate page", "Calcul years"),
                                             output_label=QCoreApplication.translate("Real estate page", "Years of loan ="),
                                             widget_name="year_finder")

        self.output_text = QCoreApplication.translate("Real estate page", "Years of loan = {result}")

    @Slot()
    @RealEstatePage.launch_simulation_security
    def launch_simulation(self):
        # Loan = Surface * surface_rate * (1 + notary_rate) - contribution
        loan = self._get_value_input(self.lineEdit_input_1) * self._get_value_input(self.lineEdit_input_2)\
               * (1 + self._get_value_input(self.notary_rate_comboBox)) - self._get_value_input(self.lineEdit_input_3)
        interest_rate = self._get_value_input(self.lineEdit_input_5) / 100
        annual_payment = 12 * self._get_value_input(self.lineEdit_input_4)

        self.simulator.sig_launch_simulation.emit("year", [loan, interest_rate, annual_payment])

    def retranslate_page(self):
        input_1 = QCoreApplication.translate("Real estate page", "House size (m²)")
        input_2 = QCoreApplication.translate("Real estate page", "Surface rate price (€/m²)").replace("€", common.MONEY_UNIT)
        input_3 = QCoreApplication.translate("Real estate page", "Contribution (€)").replace("€", common.MONEY_UNIT)
        input_4 = QCoreApplication.translate("Real estate page", "Monthly payment (€/month)").replace("€", common.MONEY_UNIT)
        input_5 = QCoreApplication.translate("Real estate page", "Interest rate (%)")
        calcul_button = QCoreApplication.translate("Real estate page", "Calcul years")
        output_label = QCoreApplication.translate("Real estate page", "Years of loan =")
        self.output_text = QCoreApplication.translate("Real estate page", "Years of loan = {result}")
        self.output_result = self.simulator.get_translate_year()

        self.retranslate(input_1, input_2, input_3, input_4, input_5, calcul_button, output_label)

    @staticmethod
    def get_init_output_label():
        return QCoreApplication.translate("Real estate page", "Years of loan =")


class HouseSizeFinderPage(RealEstatePage):

    def __init__(self):
        super(HouseSizeFinderPage, self).__init__(input_label_1=QCoreApplication.translate("Real estate page", "Surface rate price (€/m²)"),
                                                  input_label_2=QCoreApplication.translate("Real estate page", "Contribution (€)"),
                                                  input_label_3=QCoreApplication.translate("Real estate page", "Monthly payment (€/month)"),
                                                  input_label_4=QCoreApplication.translate("Real estate page", "Interest rate (%)"),
                                                  input_label_5=QCoreApplication.translate("Real estate page", "Years of loan"),
                                                  calcul_button=QCoreApplication.translate("Real estate page", "Calcul house size"),
                                                  output_label=QCoreApplication.translate("Real estate page", "House size ="),
                                                  widget_name="house_size_finder")
        self.output_text = QCoreApplication.translate("Real estate page", "House size = {result} m²")

    @Slot()
    @RealEstatePage.launch_simulation_security
    def launch_simulation(self):
        surface_rate_price = self._get_value_input(self.lineEdit_input_1)
        notary_rate = self._get_value_input(self.notary_rate_comboBox)
        contribution = self._get_value_input(self.lineEdit_input_2)
        annual_payment = 12 * self._get_value_input(self.lineEdit_input_3)
        interest_rate = self._get_value_input(self.lineEdit_input_4) / 100
        target_years = self._get_value_input(self.lineEdit_input_5)

        self.simulator.sig_launch_simulation.emit("house size", [surface_rate_price, notary_rate, contribution,
                                                                 annual_payment, interest_rate, target_years])

    def retranslate_page(self):
        input_1 = QCoreApplication.translate("Real estate page", "Surface rate price (€/m²)").replace("€", common.MONEY_UNIT)
        input_2 = QCoreApplication.translate("Real estate page", "Contribution (€)").replace("€", common.MONEY_UNIT)
        input_3 = QCoreApplication.translate("Real estate page", "Monthly payment (€/month)").replace("€", common.MONEY_UNIT)
        input_4 = QCoreApplication.translate("Real estate page", "Interest rate (%)")
        input_5 = QCoreApplication.translate("Real estate page", "Years of loan")
        calcul_button = QCoreApplication.translate("Real estate page", "Calcul house size")
        output_label = QCoreApplication.translate("Real estate page", "House size =")
        self.output_text = QCoreApplication.translate("Real estate page", "House size = {result} m²")

        self.retranslate(input_1, input_2, input_3, input_4, input_5, calcul_button, output_label)

    @staticmethod
    def get_init_output_label():
        return QCoreApplication.translate("Real estate page", "House size =")


class ContributionFinderPage(RealEstatePage):

    def __init__(self):
        super(ContributionFinderPage, self).__init__(input_label_1=QCoreApplication.translate("Real estate page", "House size (m²)"),
                                                     input_label_2=QCoreApplication.translate("Real estate page", "Surface rate price (€/m²)"),
                                                     input_label_3=QCoreApplication.translate("Real estate page", "Monthly payment (€/month)"),
                                                     input_label_4=QCoreApplication.translate("Real estate page", "Interest rate (%)"),
                                                     input_label_5=QCoreApplication.translate("Real estate page", "Years of loan"),
                                                     calcul_button=QCoreApplication.translate("Real estate page", "Calcul contribution"),
                                                     output_label=QCoreApplication.translate("Real estate page", "Contribution ="),
                                                     widget_name="contribution_finder")
        self.output_text = QCoreApplication.translate("Real estate page", "Contribution = {result} €")

    @Slot()
    @RealEstatePage.launch_simulation_security
    def launch_simulation(self):
        house_price = self._get_value_input(self.lineEdit_input_1)*self._get_value_input(self.lineEdit_input_2)
        notary_rate = self._get_value_input(self.notary_rate_comboBox)
        annual_payment = 12 * self._get_value_input(self.lineEdit_input_3)
        interest_rate = self._get_value_input(self.lineEdit_input_4) / 100
        target_years = self._get_value_input(self.lineEdit_input_5)

        self.simulator.sig_launch_simulation.emit("contribution", [house_price, notary_rate, annual_payment,
                                                                   interest_rate, target_years])

    def retranslate_page(self):
        input_1 = QCoreApplication.translate("Real estate page", "House size (m²)")
        input_2 = QCoreApplication.translate("Real estate page", "Surface rate price (€/m²)").replace("€", common.MONEY_UNIT)
        input_3 = QCoreApplication.translate("Real estate page", "Monthly payment (€/month)").replace("€", common.MONEY_UNIT)
        input_4 = QCoreApplication.translate("Real estate page", "Interest rate (%)")
        input_5 = QCoreApplication.translate("Real estate page", "Years of loan")
        calcul_button = QCoreApplication.translate("Real estate page", "Calcul contribution")
        output_label = QCoreApplication.translate("Real estate page", "Contribution =")
        self.output_text = QCoreApplication.translate("Real estate page", "Contribution = {result} €").replace("€", common.MONEY_UNIT)

        self.retranslate(input_1, input_2, input_3, input_4, input_5, calcul_button, output_label)

    @staticmethod
    def get_init_output_label():
        return QCoreApplication.translate("Real estate page", "Contribution =")


class MonthlyPaymentFinderPage(RealEstatePage):

    def __init__(self):
        super(MonthlyPaymentFinderPage, self).__init__(input_label_1=QCoreApplication.translate("Real estate page", "House size (m²)"),
                                                       input_label_2=QCoreApplication.translate("Real estate page", "Surface rate price (€/m²)"),
                                                       input_label_3=QCoreApplication.translate("Real estate page", "Contribution (€)"),
                                                       input_label_4=QCoreApplication.translate("Real estate page", "Interest rate (%)"),
                                                       input_label_5=QCoreApplication.translate("Real estate page", "Years of loan"),
                                                       calcul_button=QCoreApplication.translate("Real estate page", "Calcul monthly payment"),
                                                       output_label=QCoreApplication.translate("Real estate page", "Monthly payment ="),
                                                       widget_name="monthly_payment_finder")
        self.output_text = QCoreApplication.translate("Real estate page", "Monthly payment = {result} €/month")

    @Slot()
    @RealEstatePage.launch_simulation_security
    def launch_simulation(self):
        # Loan = Surface * surface_rate * (1 + notary_rate) - contribution
        loan = self._get_value_input(self.lineEdit_input_1) * self._get_value_input(self.lineEdit_input_2) \
               * (1 + self._get_value_input(self.notary_rate_comboBox)) - self._get_value_input(self.lineEdit_input_3)
        interest_rate = self._get_value_input(self.lineEdit_input_4) / 100
        target_years = self._get_value_input(self.lineEdit_input_5)

        self.simulator.sig_launch_simulation.emit("monthly payment", [loan, interest_rate, target_years])

    def retranslate_page(self):
        input_1 = QCoreApplication.translate("Real estate page", "House size (m²)")
        input_2 = QCoreApplication.translate("Real estate page", "Surface rate price (€/m²)").replace("€", common.MONEY_UNIT)
        input_3 = QCoreApplication.translate("Real estate page", "Contribution (€)").replace("€", common.MONEY_UNIT)
        input_4 = QCoreApplication.translate("Real estate page", "Interest rate (%)")
        input_5 = QCoreApplication.translate("Real estate page", "Years of loan")
        calcul_button = QCoreApplication.translate("Real estate page", "Calcul monthly payment")
        output_label = QCoreApplication.translate("Real estate page", "Monthly payment =")
        self.output_text = QCoreApplication.translate("Real estate page", "Monthly payment = {result} €/month").replace("€", common.MONEY_UNIT)

        self.retranslate(input_1, input_2, input_3, input_4, input_5, calcul_button, output_label)

    @staticmethod
    def get_init_output_label():
        return QCoreApplication.translate("Real estate page", "Monthly payment =")


class InterestRateFinderPage(RealEstatePage):

    def __init__(self):
        super(InterestRateFinderPage, self).__init__(input_label_1=QCoreApplication.translate("Real estate page", "House size (m²)"),
                                                     input_label_2=QCoreApplication.translate("Real estate page", "Surface rate price (€/m²)"),
                                                     input_label_3=QCoreApplication.translate("Real estate page", "Contribution (€)"),
                                                     input_label_4=QCoreApplication.translate("Real estate page", "Monthly payment (€/month)"),
                                                     input_label_5=QCoreApplication.translate("Real estate page", "Years of loan"),
                                                     calcul_button=QCoreApplication.translate("Real estate page", "Calcul interest rate"),
                                                     output_label=QCoreApplication.translate("Real estate page", "Interest rate ="),
                                                     widget_name="interest_rate_finder")
        self.output_text = QCoreApplication.translate("Real estate page", "Interest rate = {result} %")

    @Slot()
    @RealEstatePage.launch_simulation_security
    def launch_simulation(self):
        # Loan = Surface * surface_rate * (1 + notary_rate) - contribution
        loan = self._get_value_input(self.lineEdit_input_1) * self._get_value_input(self.lineEdit_input_2) \
               * (1 + self._get_value_input(self.notary_rate_comboBox)) - self._get_value_input(self.lineEdit_input_3)
        annual_payment = 12 * self._get_value_input(self.lineEdit_input_4)
        target_years = self._get_value_input(self.lineEdit_input_5)

        self.simulator.sig_launch_simulation.emit("interest rate", [loan, annual_payment, target_years])

    def retranslate_page(self):
        input_1 = QCoreApplication.translate("Real estate page", "House size (m²)")
        input_2 = QCoreApplication.translate("Real estate page", "Surface rate price (€/m²)").replace("€", common.MONEY_UNIT)
        input_3 = QCoreApplication.translate("Real estate page", "Contribution (€)").replace("€", common.MONEY_UNIT)
        input_4 = QCoreApplication.translate("Real estate page", "Monthly payment (€/month)").replace("€", common.MONEY_UNIT)
        input_5 = QCoreApplication.translate("Real estate page", "Years of loan")
        calcul_button = QCoreApplication.translate("Real estate page", "Calcul interest rate")
        output_label = QCoreApplication.translate("Real estate page", "Interest rate =")
        self.output_text = QCoreApplication.translate("Real estate page", "Interest rate = {result} %")

        self.retranslate(input_1, input_2, input_3, input_4, input_5, calcul_button, output_label)

    @staticmethod
    def get_init_output_label():
        return QCoreApplication.translate("Real estate page", "Interest rate =")
