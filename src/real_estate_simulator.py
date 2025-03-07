# Coding UTF-8

# Imports
from matplotlib import pyplot as plt
from math import ceil
from functools import wraps

import os

# # Maximum house size of model in m²
# os.environ["MAX HOUSE SIZE"] = "1000"
# # Maximum contribution of model in €
# os.environ["MAX CONTRIBUTION"] = "1000000"
# # Maximum monthly payment in €/month
# os.environ["MAX MONTHLY PAYMENT"] = "120000"
# # Maximum interest rate
# os.environ["MAX INTEREST RATE"] = "0.1"

# Maximum house size of model in m²
MAX_HOUSE_SIZE = 1000
# Maximum contribution of model in €
MAX_CONTRIBUTION = 10**6
# Maximum monthly payment in €/month
MAX_MONTHLY_PAYMENT = 12 * 10**4
# Maximum interest rate
MAX_INTEREST_RATE = 0.1


# Code
def monetary_value(value):
    """Give monetary value in euros

    :param value: int/float value
    :return: rounded 2 float value in euros
    """
    round_number = 2
    return round(value, round_number)


class RealEstateError(Exception):
    """Error in real estate simulation"""

    pass


class RealEstatePurchaseSimulator:
    """Simulator to find different value in real estate"""

    # Convergence Newton model parameter
    EPSILON = 10**-6

    # Dictionary to link environment variable to method
    DICT_MAX_VALUE = {
        "MAX_HOUSE_SIZE": "find_house_size",
        "MAX_CONTRIBUTION": "find_contribution",
        "MAX_MONTHLY_PAYMENT": "find_monthly_payment",
        "MAX_INTEREST_RATE": "find_interest_rate",
    }

    def __init__(self):
        self.loan_payment = []
        self.interest_payment = []
        self.loan_payment_cumulated = []
        self.interest_payment_cumulated = []
        self.year = 0
        self.newton_result_model = 0
        self.too_expansive_error = False
        # Maximum value of target in Newton model
        self.maximum_value = 0

    def raise_payment_error(self, expansive):
        self.too_expansive_error = expansive
        if expansive:
            raise RealEstateError("Payment error, payment is to weak or interest rate/house price is to height !")
        else:
            raise RealEstateError("Payment error, customer can not ask for loan")

    def keep_loan_interest_statistic(self, loan, interest, cumulated_loan, cumulated_interest):
        """Save interest and loan statistic of the current year.
        :params loan: float loan refund in €
        :params interest: float interest refund in €
        :params cumulated_loan: float cumulated_loan_payment in €
        :params cumulated_interest: float cumulated_interest_payment in €
        """
        self.loan_payment.append(loan)
        self.interest_payment.append(interest)
        self.loan_payment_cumulated.append(cumulated_loan)
        self.interest_payment_cumulated.append(cumulated_interest)

    def display_loan_interest_statistic(self):
        year_list = [i for i in range(1, ceil(self.year) + 1)]
        # Calcul ratio in percentage
        loan_ratio = [self.loan_payment[i] / (self.loan_payment[i] + self.interest_payment[i]) for i in range(len(self.loan_payment))]
        interest_ratio = [self.interest_payment[i] / (self.loan_payment[i] + self.interest_payment[i]) for i in range(len(self.interest_payment))]
        # Display loan/interest ratio
        plt.figure(1)
        plt.title("Loan/interest ratio depending on years")
        plt.bar(year_list, loan_ratio, label="Loan", color="skyblue")
        plt.bar(year_list, interest_ratio, bottom=loan_ratio, label="Interest", color="lightcoral")
        plt.xlabel("Years")
        plt.ylabel("Ratio (%)")
        plt.xticks(year_list)
        plt.tight_layout()
        plt.legend(loc="best")
        # Display cumulated loan and interest
        plt.figure(2)
        plt.title("Cumulated expense depending on years")
        plt.plot(year_list, self.loan_payment_cumulated, label="cumulated loan", color="blue", marker="o")
        plt.plot(year_list, self.interest_payment_cumulated, label="cumulated interest", color="red", marker="o")
        plt.xlabel("Years")
        plt.ylabel("Cumulated expense (€)")
        plt.grid(True)
        plt.tight_layout()
        plt.legend(loc="best")

        plt.show()

    def find_years(self, loan, interest_rate, annual_payment):
        """Find years of loan.

        :params loan: float loan in €
        :params interest_rate: float interest_rate not in %
        :params annual_payment: float payment in €/year
        """
        # Reset statistic
        self.loan_payment = []
        self.interest_payment = []
        self.loan_payment_cumulated = []
        self.interest_payment_cumulated = []
        year = 0
        remaining_loan = loan
        # Customer can not refund loan
        if interest_rate * remaining_loan >= annual_payment:
            self.raise_payment_error(True)
        # Customer can not ask for loan
        if remaining_loan <= 0:
            self.raise_payment_error(False)
        cumulated_loan_payment = 0
        cumulated_interest_payment = 0
        while remaining_loan > (annual_payment - interest_rate * remaining_loan):
            # Find interest and loan refund
            interest_refund = interest_rate * remaining_loan
            loan_refund = annual_payment - interest_refund
            # Update remaining loan
            remaining_loan -= loan_refund
            # Keep loan and interest statistics
            cumulated_loan_payment += loan_refund
            cumulated_interest_payment += interest_refund
            self.keep_loan_interest_statistic(loan_refund, interest_refund, cumulated_loan_payment, cumulated_interest_payment)
            year += 1
        # Customer pays loan and interest, but it's less than annual_payment
        interest_refund = interest_rate * remaining_loan
        loan_refund = remaining_loan
        cumulated_loan_payment += loan_refund
        cumulated_interest_payment += interest_refund
        self.keep_loan_interest_statistic(loan_refund, interest_refund, cumulated_loan_payment, cumulated_interest_payment)
        year += loan_refund / annual_payment
        self.year = year

    @staticmethod
    def newton_model(max_value):
        def actual_decorator(function):
            @wraps(function)
            def wrapper(self, *args, **kwargs):
                try:
                    # Init left and right surface value
                    self.maximum_value = max_value
                    left_value = 0
                    right_value = max_value
                    self.year = -1  # Initial value to trigger while loop
                    result, left_value = function(self, *args, **kwargs, left_value=left_value, right_value=right_value)
                    self.newton_result_model = result
                    if max_value - left_value < self.EPSILON:
                        raise RealEstateError("Model can not converge under max value")
                except RealEstateError as exc:
                    raise RealEstateError(exc)

            return wrapper

        return actual_decorator

    # @newton_model(max_value=int(os.environ["MAX HOUSE SIZE"]))
    @newton_model(max_value=MAX_HOUSE_SIZE)
    def find_house_size(
        self,
        surface_rate_price,
        notary_rate,
        contribution,
        annual_payment,
        interest_rate,
        target_years,
        right_value,
        left_value,
    ):
        """Find house size.

        :params surface_rate_price: float surface rate price in €/m²
        :params notary_rate: float notary rate not in %
        :params contribution: float contribution in €
        :params annual_payment: float payment in €/year
        :params interest_rate: float interest_rate not in %
        :params target_years: float target years
        :params maximum_surface: float maximum surface to find, default value is 300 m²
        """
        while abs(self.year - target_years) > self.EPSILON and right_value - left_value > self.EPSILON:
            current_surface = (right_value + left_value) / 2
            loan = surface_rate_price * current_surface * (1 + notary_rate) - contribution
            left_value, right_value = self.update_left_right_value(
                loan,
                interest_rate,
                annual_payment,
                value=current_surface,
                left_value=left_value,
                right_value=right_value,
                positive_derivative=True,
                target_year=target_years,
            )
        return current_surface, left_value

    # @newton_model(max_value=int(os.environ["MAX CONTRIBUTION"]))
    @newton_model(max_value=MAX_CONTRIBUTION)
    def find_contribution(self, house_price, notary_rate, annual_payment, interest_rate, target_years, right_value, left_value):
        """Find contribution.

        :params house_price: float house price in €
        :params notary_rate: float notary rate not in %
        :params annual_payment: float payment in €/year
        :params interest_rate: float interest_rate not in %
        :params target_years: int target years
        """
        while abs(self.year - target_years) > self.EPSILON and right_value - left_value > self.EPSILON:
            current_contribution = (right_value + left_value) / 2
            loan = house_price * (1 + notary_rate) - current_contribution
            left_value, right_value = self.update_left_right_value(
                loan,
                interest_rate,
                annual_payment,
                value=current_contribution,
                left_value=left_value,
                right_value=right_value,
                positive_derivative=False,
                target_year=target_years,
            )
        return current_contribution, left_value

    @newton_model(max_value=MAX_MONTHLY_PAYMENT)
    def find_monthly_payment(self, loan, interest_rate, target_years, right_value, left_value):
        """Find annual payment.

        :params loan: float loan price in €
        :params interest_rate: float interest_rate not in %
        :params target_years: int target years
        """
        while abs(self.year - target_years) > self.EPSILON and right_value - left_value > self.EPSILON:
            current_annual_payment = (right_value + left_value) / 2
            left_value, right_value = self.update_left_right_value(
                loan,
                interest_rate,
                current_annual_payment,
                value=current_annual_payment,
                left_value=left_value,
                right_value=right_value,
                positive_derivative=False,
                target_year=target_years,
            )
        return current_annual_payment / 12, left_value

    @newton_model(max_value=MAX_INTEREST_RATE)
    def find_interest_rate(self, loan, annual_payment, target_years, right_value, left_value):
        """Find interest rate.

        :params loan: float loan price in €
        :params annual_payment: float annual payment in €/year
        :params target_years: int target years
        """
        while abs(self.year - target_years) > self.EPSILON and right_value - left_value > self.EPSILON:
            current_interest_rate = (right_value + left_value) / 2
            left_value, right_value = self.update_left_right_value(
                loan,
                current_interest_rate,
                annual_payment,
                value=current_interest_rate,
                left_value=left_value,
                right_value=right_value,
                positive_derivative=True,
                target_year=target_years,
            )
        return current_interest_rate, left_value

    def update_left_right_value(self, loan, interest_rate, annual_payment, value, left_value, right_value, positive_derivative, target_year):
        """Calcul years of loan, then update left and right value in Newton algorithm according to value derivative.
        :params loan: float loan price in €
        :params interest_rate: float interest rate not in %
        :params annual_payment: float annual payment in €/year
        :params value: float/int value to find with Newton algorithm
        :params left_value: float/int left value (low value born)
        :params right_value: float/int right value (height value born)
        :params positive_derivative: boolean corresponding to sign of derivative,
        if up off value increase loan, positive_derivative is True,
        if down off value decrease loan, positive_derivative is False.
        :params target_year: int target year of loan
        :returns: right and left updated value
        """
        # Init left and right value
        r_value, l_value = right_value, left_value
        try:
            self.find_years(loan, interest_rate, annual_payment)  # Update self.year
        except Exception:
            # (Loan is too height + positive derivative) or (Loan is too low + negative derivative)
            if self.too_expansive_error == positive_derivative:
                # Low value
                r_value = value
            # (Loan is too height + negative derivative) or (Loan is too low + positive derivative)
            else:
                # Up value
                l_value = value
        else:
            # (Loan is too height + positive derivative) or (Loan is too low + negative derivative)
            if (self.year > target_year) == positive_derivative:
                # Low value
                r_value = value
            # (Loan is too height + negative derivative) or (Loan is too low + positive derivative)
            else:
                # Up value
                l_value = value
        return l_value, r_value

    def refresh_model(self, money_factor):
        # Update find method of Newton model with current max environment variable
        for max_variable_name, func in self.DICT_MAX_VALUE.items():
            # Recalculate max value which contains € in unit
            if max_variable_name in ("MAX_CONTRIBUTION", "MAX_MONTHLY_PAYMENT"):
                max_value = int(globals().get(max_variable_name) * money_factor)
            else:
                max_value = globals().get(max_variable_name)
            find_func = getattr(self, func)
            decorated_method = self.newton_model(max_value)(find_func.__wrapped__)
            new_find_func = decorated_method.__get__(self, self.__class__)
            # Save new method
            setattr(self, func, new_find_func)


if __name__ == "__main__":
    # Constants
    # House price
    SURFACE_RATE_PRICE = 2500  # in €/m²
    SURFACE = 100  # in m²
    HOUSE_PRICE = SURFACE_RATE_PRICE * SURFACE
    # Notary fees
    NOTARY_COST_RATE = 0.08
    NOTARY_FEES = NOTARY_COST_RATE * HOUSE_PRICE
    # Loan
    TOTAL_AMOUNT_HOUSE = HOUSE_PRICE + NOTARY_FEES
    CONTRIBUTION = 80000
    LOAN = TOTAL_AMOUNT_HOUSE - CONTRIBUTION
    # Interest Rate
    INTEREST_RATE = 0.03
    # Monthly payment
    MONTHLY_PAYMENT = 1600  # in €/month
    ANNUAL_PAYMENT = 12 * MONTHLY_PAYMENT
    # Years of loan
    LOAN_YEARS = 11.9

    # Mode
    MODE = 5

    if MODE == 1:
        print(f"House price is {monetary_value(HOUSE_PRICE)}€")
        print(f"Notary fees is {monetary_value(NOTARY_FEES)}€")
        print(f"Contribution is {monetary_value(CONTRIBUTION)}€")
        print(f"Loan is {monetary_value(LOAN)}€")
        print(f"Monthly payment is {monetary_value(MONTHLY_PAYMENT)}€/month")
        print(f"Interest rate is {round(100 * INTEREST_RATE, 2)}%")

        simulation = RealEstatePurchaseSimulator()
        simulation.find_years(LOAN, INTEREST_RATE, ANNUAL_PAYMENT)
        print(f"\nYear loan = {round(simulation.year, 1)}")
        simulation.display_loan_interest_statistic()
    elif MODE == 2:
        print(f"Surface rate price is {monetary_value(SURFACE_RATE_PRICE)}€/m²")
        print(f"Contribution is {CONTRIBUTION}€")
        print(f"Monthly payment is {monetary_value(MONTHLY_PAYMENT)}€/month")
        print(f"Interest rate is {round(100 * INTEREST_RATE, 2)}%")
        print(f"Years of loan is {LOAN_YEARS}")

        simulation = RealEstatePurchaseSimulator()
        simulation.find_house_size(SURFACE_RATE_PRICE, NOTARY_COST_RATE, CONTRIBUTION, ANNUAL_PAYMENT, INTEREST_RATE, LOAN_YEARS)

        print(f"\nSurface = {simulation.newton_result_model}")
        simulation.display_loan_interest_statistic()
    elif MODE == 3:
        print(f"House price {monetary_value(HOUSE_PRICE)}€")
        print(f"Monthly payment is {monetary_value(MONTHLY_PAYMENT)}€/month")
        print(f"Interest rate is {round(100 * INTEREST_RATE, 2)}%")
        print(f"Years of loan is {LOAN_YEARS}")

        simulation = RealEstatePurchaseSimulator()
        simulation.find_contribution(HOUSE_PRICE, NOTARY_COST_RATE, ANNUAL_PAYMENT, INTEREST_RATE, LOAN_YEARS)

        print(f"\nContribution = {simulation.newton_result_model}€")
        simulation.display_loan_interest_statistic()
    elif MODE == 4:
        print(f"House price is {monetary_value(HOUSE_PRICE)}€")
        print(f"Notary fees is {monetary_value(NOTARY_FEES)}€")
        print(f"Contribution is {monetary_value(CONTRIBUTION)}€")
        print(f"Loan is {monetary_value(LOAN)}€")
        print(f"Interest rate is {round(100 * INTEREST_RATE, 2)}%")
        print(f"Years of loan is {LOAN_YEARS}")

        simulation = RealEstatePurchaseSimulator()
        simulation.find_monthly_payment(LOAN, INTEREST_RATE, LOAN_YEARS)

        print(f"\nMonthly payment = {simulation.newton_result_model}€/month")
        simulation.display_loan_interest_statistic()
    elif MODE == 5:
        print(f"House price is {monetary_value(HOUSE_PRICE)}€")
        print(f"Notary fees is {monetary_value(NOTARY_FEES)}€")
        print(f"Contribution is {monetary_value(CONTRIBUTION)}€")
        print(f"Loan is {monetary_value(LOAN)}€")
        print(f"Monthly payment is {monetary_value(MONTHLY_PAYMENT)}€/month")
        print(f"Years of loan is {LOAN_YEARS}")

        simulation = RealEstatePurchaseSimulator()
        simulation.find_interest_rate(LOAN, ANNUAL_PAYMENT, LOAN_YEARS)

        print(f"\nInterest rate = {round(100 * simulation.newton_result_model, 3)}%")
        print(f"\nCumulated interest = {simulation.interest_payment_cumulated[-1]} €")
        simulation.display_loan_interest_statistic()

""" Summary of this simulation
Mode 1: year finder
Inputs: - loan (house price + notary price - contribution)
        - annual payment
        - interest rate
Outputs:    - years
            - interest

Mode 2: size finder
Inputs: - surface rate price (related to localisation)
        - contribution
        - monthly payment
        - interest rate
        - years
Outputs:    - house size
            - loan
            - interest

Mode 3: contribution finder
Inputs: - house price
        - monthly payment
        - interest rate
        - years
Outputs:    - contribution
            - loan
            - interest

Mode 4: monthly payment finder
Inputs: - loan
        - interest rate
        - years
Outputs:    - monthly payment
            - interest

Mode 5: interest rate finder
Inputs: - loan
        - annual payment
        - years
Outputs:    - interest rate
            - interest
            

"""
