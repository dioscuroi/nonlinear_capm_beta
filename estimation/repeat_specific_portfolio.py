import sys
import shutil

from DataLoader import DataLoader
from train_portfolio_returns import train_portfolio_returns
from nonlinear_capm_beta.figures.plot_cum_beta import plot_cum_beta


def repeat_specific_portfolio(filename, portfolio, no_lags, no_repeats = 10):

    print("************************************************")
    print(" Repeat the Training of Portfolio Returns")
    print(" filename: {}".format(filename))
    print(" portfolio: {}".format(portfolio))
    print("************************************************")

    for repeat_id in range(0, no_repeats):

        print("")
        print("==== Repeat ID: {}/{} ====".format(repeat_id + 1, no_repeats))
        print("")

        train_portfolio_returns(filename, portfolio, no_lags, zero_init=False)

    return


# call the main function when called directly
if __name__ == "__main__":

    # parse parameters passed over from the command line
    if len(sys.argv) == 4:
        filename = sys.argv[1]
        portfolio = sys.argv[2]
        no_lags = int(sys.argv[3])

    else:
        filename = 'portfolio_size'
        portfolio = 'd10'
        no_lags = 1

    repeat_specific_portfolio(filename, portfolio, no_lags)

