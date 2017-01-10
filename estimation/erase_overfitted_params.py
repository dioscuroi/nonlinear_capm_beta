import sys
import numpy as np

from utils import *
from DataLoader import DataLoader


def erase_overfitted_params(year_from=1931, year_to=2015):
    """erase_overfitted_params
    """

    # initialize parameters and variables
    loader = DataLoader(connect=True)

    for year in range(year_from, year_to+1):

        print("")
        print("***********************************")
        print(" erase_overfitted_params ")
        print(" year: {}".format(year))
        print("***********************************")

        count = 0

        permno_list = loader.load_permno_list_with_parameters(year, max_rank=500)

        for permno in permno_list['permno']:

            param = loader.load_stock_params(year, permno)

            if check_if_overfitted_by_param(param):

                query = """update beta_parameters_stocks
                           set no_obs = null, sample_from = null, sample_to = null, parameters = null,
                              beta_average = null, beta_delay = null, beta_convexity = null
                           where year = {} and permno = {}""".format(year, permno)

                loader.sql_query_commit(query)

                print('*', end="", flush=True)

            else:
                print('.', end="", flush=True)

            count += 1

            if np.mod(count, 50) == 0:
                print('')

        print("")

    loader.close()


if __name__ == "__main__":

    if len(sys.argv) == 3:
        year_from = int(sys.argv[1])
        year_to = int(sys.argv[2])

    else:
        year_from = 2003
        year_to = 2015

    erase_overfitted_params(year_from, year_to)
