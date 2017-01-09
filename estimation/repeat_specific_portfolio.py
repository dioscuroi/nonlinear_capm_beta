import sys
import shutil

from DataLoader import DataLoader
from train_portfolio_returns import train_portfolio_returns
from nonlinear_capm_beta.figures.plot_cum_beta import plot_cum_beta


def repeat_specific_portfolio(freq="monthly", portfolio='small-growth'):

    print("************************************************")
    print(" Repeat the Training of Portfolio Returns")
    print(" freq: {}".format(freq))
    print(" portfolio: {}".format(portfolio))
    print("************************************************")

    loader = DataLoader(connect=True)

    no_repeats = 10

    for repeat_id in range(0, no_repeats):

        print("")
        print("==== Repeat ID: {}/{} ====".format(repeat_id, no_repeats))
        print("")

        train_portfolio_returns(freq, portfolio)

        plot_cum_beta(freq, portfolio)

        source = "outputs/plot_cum_beta_{}_{}.csv".format(freq, portfolio)
        dest = "outputs/plot_cum_beta_{}_{}_{:02d}.csv".format(freq, portfolio, repeat_id)

        shutil.move(source, dest)

        loader.move_portfolio_params_to_the_repeated(freq, portfolio, repeat_id)


    loader.close()


# call the main function when called directly
if __name__ == "__main__":
    repeat_specific_portfolio("daily", "smb")
    repeat_specific_portfolio("daily", "hml")
    # repeat_specific_portfolio("monthly", "small-growth")
    # repeat_specific_portfolio("monthly", "small-value")
    # repeat_specific_portfolio("monthly", "large-growth")
    repeat_specific_portfolio("monthly", "smb")
    repeat_specific_portfolio("monthly", "hml")
    # repeat_specific_portfolio("monthly", "small")
