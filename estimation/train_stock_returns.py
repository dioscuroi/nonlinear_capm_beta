import sys
import time
import json
import pandas as pd

from datetime import date, datetime

from utils import *
from Trainer import Trainer
from DataLoader import DataLoader


def train_stock_returns(year_from=1936, year_to=2016, max_rank=500):

    print("***********************************")
    print(" Train Stock Returns")
    print(" year_from: {}".format(year_from))
    print(" year_to: {}".format(year_to))
    print(" max_rank: {}".format(max_rank))
    print("***********************************")

    no_lags = 5

    loader = DataLoader(connect=True)

    total_training_no = 0
    total_training_time = 0

    for year in range(year_from, year_to + 1):

        print(" ")
        print("***********************************")
        print(" Year: {}".format(year))
        print("***********************************")

        date_from = date(year-9, 1, 1)
        date_to = date(year, 12, 31)

        print("Loading market returns...")
        mktrf = loader.load_market_returns('daily', no_lags=no_lags, date_from=date_from, date_to=date_to)

        permno_list = loader.load_target_permno_list(year, max_rank)

        if permno_list is None:
            print("No observations are left in this year. Let's move on to the next year.")
            continue

        for i in range(len(permno_list)):

            permno = permno_list.loc[i, 'permno']

            print(" ")
            print("*****************************************")
            print(datetime.today())
            print(" year: {}, permno: {} ({}/{})".format(year, permno, i+1, len(permno_list)))
            print("*****************************************")

            if not loader.check_if_still_empty(year, permno):
                continue

            t_start = time.time()

            print("Loading stock returns...")
            stock_rets = loader.load_stock_returns(permno, date_from, date_to)

            if stock_rets is None:
                loader.save_stock_params_only_no_obs(year, permno, 0)
                continue

            merged = pd.merge(mktrf, stock_rets, on='date')

            no_obs = len(merged)

            if no_obs < 1000:
                print("Skip this stock due to the lack of observations (obs:{})".format(no_obs))
                loader.save_stock_params_only_no_obs(year, permno, no_obs)

                continue

            y_data = merged.loc[:,'ret']*100 - merged.loc[:,'rf']
            y_data = y_data.as_matrix().reshape(-1, 1)

            x_data = merged.iloc[:, 1:-1]
            del x_data['rf']
            x_data = x_data.as_matrix()

            # Initialize the trainer
            max_retries = 3
            zero_init = True

            for attempt_id in range(max_retries):

                trainer = Trainer(depth=2, width=1, no_inputs=no_lags+1, zero_init=zero_init)

                trainer.run_ols_regression(x_data, y_data)

                params = trainer.train(x_data, y_data, x_tolerance=1e-2, cost_tolerance=1e-3)

                del trainer

                if not check_if_overfitted_by_param(params, freq="daily", no_lags=no_lags):
                    break

                params = None
                zero_init = False

                print("Parameters are overfitted. Let's try again.")
                print("")

            # if parameters are still overfitted, replace parameters with OLS coefficients
            if params is None:
                trainer = Trainer(depth=2, width=1, no_inputs=no_lags + 1, zero_init=True)
                trainer.run_ols_regression(x_data, y_data)
                params = trainer.flush_params_to_dict()

            # compute beta
            beta = compute_beta(param=params, freq='daily', no_lags=no_lags)

            assert(not check_if_overfitted_by_beta(beta))

            beta0 = beta[:, 0]
            beta20 = np.sum(beta, axis=1)

            beta_average = np.mean(beta20)
            beta_delay = np.mean(beta20) - np.mean(beta0)
            beta_convexity = (beta20[0] + beta20[-1]) / 2 - beta20[int((len(beta20) - 1) / 2)]

            query = """
              update beta_parameters_stocks
              set no_obs = {},
                sample_from = '{}',
                sample_to = '{}',
                parameters = '{}',
                beta_average = {},
                beta_delay = {},
                beta_convexity = {}
              where year = {} and permno = {}
            """.format(no_obs, date_from, date_to,
                       json.dumps(params), beta_average, beta_delay, beta_convexity,
                       year, permno)

            loader.sql_query_commit(query)

            elapsed = time.time() - t_start

            total_training_no += 1
            total_training_time += elapsed

            print("Results:")
            print(" - permno: {}, year: {}, no_obs:{}".format(permno, year, no_obs))
            print(" - beta_average: {:.3f}, beta_delay: {:.3f}, beta_convexity: {:.3f}".format(beta_average, beta_delay, beta_convexity))
            print("")
            print("Elapsed time: {:.3f} seconds".format(elapsed))
            print("")
            print("Total training no: {}".format(total_training_no))
            print("Total training time: {:.2f} minutes ({:.2f} hours)".format(total_training_time/60, total_training_time/3600))
            print("Average training time: {:.3f} seconds".format(total_training_time / total_training_no))

    loader.close()

# call the main function when called directly
if __name__ == "__main__":

    if len(sys.argv) == 4:
        year_from = int(sys.argv[1])
        year_to = int(sys.argv[2])
        max_rank = int(sys.argv[3])

    else:
        year_from = 1936
        year_to = 2015
        max_rank = 500

    train_stock_returns(year_from, year_to, max_rank)

    print('** beep **\a')
