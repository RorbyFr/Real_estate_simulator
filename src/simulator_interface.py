from PySide6.QtCore import QObject, Signal, Slot

from real_estate_simulator import RealEstatePurchaseSimulator, RealEstateError, MAX_CONTRIBUTION, MAX_MONTHLY_PAYMENT
import common

from math import floor, ceil


class SimulatorInterface(QObject):
    sig_launch_simulation = Signal(str, list)
    sig_get_result_simulation = Signal(str)
    sig_display_result_statistic = Signal(float, list, list, list, list)
    sig_parameter_error = Signal(str)
    sig_last_error_changed = Signal(str)
    sig_refresh_model = Signal()

    # Type of error of simulation
    MODEL_ERROR = "model"
    INPUT_ERROR = "input"

    def __init__(self):
        super(SimulatorInterface, self).__init__()
        self.simulator = RealEstatePurchaseSimulator()
        self.simu_func = "func"
        self.simu_result = "result"
        self.unit_result = "unit"
        self.simulation_dict = {
            "year": {self.simu_func: self.simulator.find_years, self.simu_result: "year", self.unit_result: "years"},
            "house size": {
                self.simu_func: self.simulator.find_house_size,
                self.simu_result: "surface",
                self.unit_result: "m²",
            },
            "contribution": {
                self.simu_func: self.simulator.find_contribution,
                self.simu_result: "contribution",
                self.unit_result: "€",
            },
            "monthly payment": {
                self.simu_func: self.simulator.find_monthly_payment,
                self.simu_result: "monthly_payment",
                self.unit_result: "€/months",
            },
            "interest rate": {
                self.simu_func: self.simulator.find_interest_rate,
                self.simu_result: "interest_rate",
                self.unit_result: "%",
            },
        }
        # Last text result to translate again
        self.last_year_result = None
        # Last target of simulation to translate again year
        self.last_target = None
        # Last error of simulation to translate again year
        self.last_error = None

    def connect_all_signal(self):
        self.sig_launch_simulation.connect(self.launch_simulation)
        self.sig_last_error_changed.connect(self.last_error_changed)
        self.sig_refresh_model.connect(self.refresh_model)

    @Slot(str, list)
    def launch_simulation(self, target, simulation_parameters):
        """Launch simulation to find target value

        :params target: string target parameter to find, value can be:
        - year
        - house size
        - contribution
        - monthly payment
        - interest rate
         :params simulation_parameters: list of parameters to launch simulation
        """
        # Save target in memory before launch simulation
        self.last_target = target
        # Launch simulation
        try:
            self.simulation_dict[target][self.simu_func](*simulation_parameters)
        except RealEstateError:
            self.last_error = self.MODEL_ERROR
            # Convert maximum interest rate in %
            if target == "interest rate":
                self.simulator.maximum_value *= 100
            error_text = self.get_translated_model_error()
            self.sig_parameter_error.emit(error_text)
            return
        # Retrieve result from simulator class
        result = self.simulator.year if target == "year" else self.simulator.newton_result_model
        # Convert interest rate in percentage
        match target:
            case "year":
                year = floor(result)
                month = floor((result - year) * 12)
                day = ceil((result - year - month / 12) * 365)
                result = self.tr("{} years, {} months and {} days").format(year, month, day)
                self.last_year_result = (year, month, day)
            case "house size":
                result = round(result, 2)
            case "contribution":
                result = round(result, 2)
            case "monthly payment":
                result = round(result, 2)
            case "interest rate":
                result = round(100 * result, 3)
        # Emit signals
        self.sig_get_result_simulation.emit(str(result))
        self.sig_display_result_statistic.emit(
            self.simulator.year,
            self.simulator.loan_payment,
            self.simulator.interest_payment,
            self.simulator.loan_payment_cumulated,
            self.simulator.interest_payment_cumulated,
        )

    def get_translate_year(self):
        text = None
        if self.last_year_result is not None:
            text = self.tr("{} years, {} months and {} days").format(*self.last_year_result)
        return text

    def get_translated_error(self):
        text = ""
        if self.last_error == self.MODEL_ERROR:
            text = self.get_translated_model_error(True)
        elif self.last_error == self.INPUT_ERROR:
            text = self.get_translated_input_error()
        return text

    @staticmethod
    def get_translated_input_error(cls):
        return cls.tr("Error in input parameter detected, please check your values")

    def get_translated_model_error(self, error_pop_up_still_opened=False):
        maximum_value = self.simulator.maximum_value
        if "€" in self.simulation_dict[self.last_target][self.unit_result] and error_pop_up_still_opened:
            if self.last_target == "contribution":
                maximum_value = int(MAX_CONTRIBUTION * common.DICT_MONEY_CONVERSION[common.MONEY_UNIT])
            elif self.last_target == "monthly payment":
                maximum_value = int(MAX_MONTHLY_PAYMENT * common.DICT_MONEY_CONVERSION[common.MONEY_UNIT])
        translated_target = self.get_translated_last_target()
        return (
            self.tr("Model can not converge, maximum value {} is {} {}")
            .format(translated_target, maximum_value, self.simulation_dict[self.last_target][self.unit_result])
            .replace("€", common.MONEY_UNIT)
        )

    def get_translated_last_target(self):
        text = ""
        if self.last_target == "year":
            text = self.tr("of year")
        elif self.last_target == "house size":
            text = self.tr("of house size")
        elif self.last_target == "contribution":
            text = self.tr("of contribution")
        elif self.last_target == "monthly payment":
            text = self.tr("of monthly payment")
        elif self.last_target == "interest rate":
            text = self.tr("of interest rate")
        return text

    @Slot(str)
    def last_error_changed(self, error):
        self.last_error = error

    @Slot()
    def refresh_model(self):
        self.simulator.refresh_model(common.DICT_MONEY_CONVERSION[common.MONEY_UNIT])
        self.simulation_dict["year"][self.simu_func] = self.simulator.find_years
        self.simulation_dict["house size"][self.simu_func] = self.simulator.find_house_size
        self.simulation_dict["contribution"][self.simu_func] = self.simulator.find_contribution
        self.simulation_dict["monthly payment"][self.simu_func] = self.simulator.find_monthly_payment
        self.simulation_dict["interest rate"][self.simu_func] = self.simulator.find_interest_rate
