import sys
import time
import pandas as pd

from datetime import date, datetime

from Trainer import Trainer
from DataLoader import DataLoader


def train_stock_returns(year_from=1931, year_to=2016, max_rank=500):

    print("***********************************")
    print(" Train Stock Returns")
    print(" year_from: {}".format(year_from))
    print(" year_to: {}".format(year_to))
    print(" max_rank: {}".format(max_rank))
    print("***********************************")

    # Load market returns
    loader = DataLoader(connect=True)

    total_training_no = 0
    total_training_time = 0

    for year in range(year_from, year_to + 1):

        print(" ")
        print("***********************************")
        print(" Year: {}".format(year))
        print("***********************************")

        date_from = date(year-4, 1, 1)
        date_to = date(year, 12, 31)

        print("Loading market returns...")
        mktrf = loader.load_market_returns('daily', date_from=date_from, date_to=date_to)

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

            merged = pd.merge(mktrf, stock_rets, on='date')

            no_obs = len(merged)

            print("No of matched observations: {}".format(no_obs))

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
            try:
                trainer = Trainer(depth=2, width=1, no_inputs=21, zero_init=True)

                trainer.run_ols_regression(x_data, y_data)

                # launch the learning
                params = trainer.train(x_data, y_data)

                loader.save_stock_params(year, permno, no_obs, date_from, date_to, params)

                del trainer

            except:
                print("Unexpected error: ", sys.exc_info()[0])
                print("Skip this permno and move on to the next one")

            elapsed = time.time() - t_start

            total_training_no += 1
            total_training_time += elapsed

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

        train_stock_returns(year_from, year_to, max_rank)

    else:
        train_stock_returns()

    print('** beep **\a')
