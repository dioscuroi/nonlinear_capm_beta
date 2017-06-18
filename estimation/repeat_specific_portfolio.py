import sys
import shutil

from DataLoader import DataLoader
from train_portfolio_returns import train_portfolio_returns
from nonlinear_capm_beta.figures.plot_cum_beta import plot_cum_beta


def repeat_specific_portfolio(filename, portfolio, no_lags):

    print("************************************************")
    print(" Repeat the Training of Portfolio Returns")
    print(" filename: {}".format(filename))
    print(" portfolio: {}".format(portfolio))
    print("************************************************")

    no_repeats = 10

    for repeat_id in range(0, no_repeats):

        print("")
        print("==== Repeat ID: {}/{} ====".format(repeat_id, no_repeats))
        print("")

        train_portfolio_returns(filename, portfolio, no_lags, zero_init=False)

    return


# call the main function when called directly
if __name__ == "__main__":

    repeat_specific_portfolio('ff3factors_daily', 'smb', 20)
    repeat_specific_portfolio('ff3factors_daily', 'hml', 20)

