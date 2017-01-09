import sys
import numpy as np
import matplotlib.pyplot as plt

from Trainer import Trainer
from DataLoader import DataLoader


def compute_stock_beta(year_from=1931, year_to=2015):
    """compute_stock_beta
    """

    # initialize parameters and variables
    max_rank = 500

    no_lags = 20

    mktrf = np.arange(-3, 3 + 0.001, .1)

    x_data = np.zeros([len(mktrf), no_lags + 1])

    for i in range(0, no_lags + 1):
        x_data[:, i] = mktrf

    trainer = Trainer()

    loader = DataLoader(connect=True)

    for year in range(1931,2016):

        print("")
        print("***********************************")
        print(" compute_stock_beta ")
        print(" year: {}".format(year))
        print("***********************************")

        count = 0

        permno_list = loader.load_permno_list_with_parameters(year, max_rank)

        for permno in permno_list['permno']:

            print('.', end="", flush=True)

            count += 1

            if np.mod(count, 50) == 0:
                print('')

            param = loader.load_stock_params(year, permno)

            trainer.load_parameters(param)

            [_, beta] = trainer.derive_expret_beta(x_data)

            beta = beta[0]

            if np.any(np.isnan(beta)):
                continue

            beta0 = beta[:,0]
            beta20 = np.sum(beta, axis=1)

            beta_average = np.mean(beta20)
            beta_stdev = np.std(beta20)
            beta_delay = np.mean(beta20) - np.mean(beta0)
            beta_convexity = (beta20[0] + beta20[-1])/2 - beta20[int((len(beta20)-1)/2)]

            if beta_stdev > 0.1:
                normalized = (beta20 - beta_average) / beta_stdev
            else:
                normalized = 0

            # this is very likely to be an over-fitting
            if np.any(np.abs(normalized) > 3):
                # plt.plot(mktrf, np.concatenate((beta0.reshape(-1,1), beta20.reshape(-1,1)), axis=1))
                # plt.clf()
                continue

            try:
                loader.save_beta_stats(year, permno, beta_average, beta_delay, beta_convexity)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                print("year: {}, permno: {}".format(year, permno))
                print("- average: {}, delay: {}, convexity: {}".format(beta_average, beta_delay, beta_convexity))

        print("")

    loader.close()


if __name__ == "__main__":
    compute_stock_beta(1931, 2015)
