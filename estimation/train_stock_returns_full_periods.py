import sys
import time
import json
import pandas as pd

from datetime import date, datetime

from utils import *
from Trainer import Trainer
from DataLoader import DataLoader


def train_stock_returns_full_periods(permno_from, permno_to):

    print("***********************************")
    print(" Train Stock Returns")
    print(" permno_from: {}".format(permno_from))
    print(" permno_to  : {}".format(permno_to))
    print("***********************************")

    no_lags = 10

    loader = DataLoader(connect=True)

    total_training_no = 0
    total_training_time = 0

    print("Loading market returns...")
    mktrf = loader.load_market_returns('daily', no_lags=no_lags)

    print("Loading untouched firm list...")
    query = """
        select permno, obs
        from beta_stocks_full_periods
        where permno >= {} and permno <= {} and touched is null
        order by permno
    """.format(permno_from, permno_to)

    permno_list = loader.sql_query_select(query)

    if permno_list is None:
        print("Cannot find any untouched firm for permno between {} and {}".format(permno_from, permno_to))
        return

    for i in range(len(permno_list)):

        permno = permno_list.loc[i, 'permno']

        print(" ")
        print("*****************************************")
        print(datetime.today())
        print("permno: {} ({}/{})".format(permno, i+1, len(permno_list)))
        print("*****************************************")

        t_start = time.time()

        # load stock returns
        print("Loading stock returns...")
        stock_rets = loader.load_stock_returns(permno)

        merged = pd.merge(mktrf, stock_rets, on='date')

        no_obs = len(merged)

        print("# observations: {}".format(no_obs))

        if no_obs < 100:
            print("Skip this stock due to the lack of observations (obs:{})".format(no_obs))
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

            zero_init = False

            print("Parameters are overfitted. Let's try again.")
            print("")

        # compute beta
        beta = compute_beta(param=params, freq='daily', no_lags=no_lags)

        if check_if_overfitted_by_beta(beta):
            print("Parameters are still overfitted after {} retries. Give up this observation.".format(max_retries))

            # mark the permno as touched
            query = "update beta_stocks_full_periods set touched = now() where permno = {}".format(permno)
            loader.sql_query_commit(query)

            continue

        beta0 = beta[:, 0]
        beta20 = np.sum(beta, axis=1)

        beta_average = np.mean(beta20)
        beta_delay = np.mean(beta20) - np.mean(beta0)
        beta_convexity = (beta20[0] + beta20[-1]) / 2 - beta20[int((len(beta20) - 1) / 2)]

        query = """
            update beta_stocks_full_periods
            set touched = now(),
              parameters = '{}',
              beta_average = {},
              beta_delay = {},
              beta_convexity = {}
            where permno = {}
        """.format(json.dumps(params), beta_average, beta_delay, beta_convexity, permno)

        loader.sql_query_commit(query)

        print("** Parameters are well estiamted!! Hooray!! **")
        print("")

        elapsed = time.time() - t_start
        print("Elapsed time: {:.3f} seconds".format(elapsed))

        total_training_no += 1
        total_training_time += elapsed

    print("")
    print("Total training no: {}".format(total_training_no))
    print("Total training time: {:.2f} minutes ({:.2f} hours)".format(total_training_time/60, total_training_time/3600))
    print("Average training time: {:.3f} seconds".format(total_training_time / total_training_no))

    loader.close()

# call the main function when called directly
if __name__ == "__main__":

    if len(sys.argv) == 3:
        permno_from = int(sys.argv[1])
        permno_to = int(sys.argv[2])

    else:
        permno_from = 10000
        permno_to = 99999

    train_stock_returns_full_periods(permno_from, permno_to)

    print('\n\n')
    print('** beep **\a')
