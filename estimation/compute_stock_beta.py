import sys
import numpy as np

from utils import *
from DataLoader import DataLoader


def compute_stock_beta(year_from=1931, year_to=2015):
    """compute_stock_beta
    """

    # initialize parameters and variables
    loader = DataLoader(connect=True)

    for year in range(year_from, year_to+1):

        print("")
        print("***********************************")
        print(" compute_stock_beta ")
        print(" year: {}".format(year))
        print("***********************************")

        count = 0

        permno_list = loader.load_permno_list_with_parameters(year, max_rank=500)

        if permno_list is None:
            continue

        for permno in permno_list['permno']:

            print('.', end="", flush=True)

            count += 1

            if np.mod(count, 50) == 0:
                print('')

            param = loader.load_stock_params(year, permno)

            beta = compute_beta(param=param, freq='daily', no_lags=10)

            if check_if_overfitted_by_beta(beta):
                continue

            beta0 = beta[:,0]
            beta20 = np.sum(beta, axis=1)

            beta_average = np.mean(beta20)
            beta_delay = np.mean(beta20) - np.mean(beta0)
            beta_convexity = (beta20[0] + beta20[-1])/2 - beta20[int((len(beta20)-1)/2)]

            try:
                loader.save_beta_stats(year, permno, beta_average, beta_delay, beta_convexity)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                print("year: {}, permno: {}".format(year, permno))
                print("- average: {}, delay: {}, convexity: {}".format(beta_average, beta_delay, beta_convexity))

        print("")

    loader.close()


if __name__ == "__main__":

    if len(sys.argv) == 3:
        year_from = int(sys.argv[1])
        year_to = int(sys.argv[2])

    else:
        year_from = 1936
        year_to = 2015

    compute_stock_beta(year_from, year_to)

    print('** beep **\a')
