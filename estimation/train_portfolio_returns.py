import sys
import numpy as np
import pandas as pd

from Trainer import Trainer
from DataLoader import DataLoader


def train_portfolio_returns(freq='monthly', depth=2, width=1, portfolio_name = None):

    print("***********************************")
    print(" Train Portfolio Returns")
    print(" freq: {}".format(freq))
    print(" depth: {}, width: {}".format(depth, width))
    print("***********************************")

    if freq == 'daily':
        no_lags = 20
        log_returns = False
    else:
        no_lags = 1
        log_returns = True

    # Load market returns
    loader = DataLoader(connect=True)

    mktrf = loader.load_market_returns(freq, no_lags=no_lags, log_returns=log_returns)

    # now run the machine learning on portfolio returns
    if portfolio_name is None:
        portfolio_list = ['small', 'large', 'growth', 'value', 'smb', 'hml']

        if freq == 'monthly':
            portfolio_list.extend(['small_growth', 'small_value', 'large_growth', 'large_value'])

    else:
        portfolio_list = [portfolio_name]

    for portfolio in portfolio_list:

        print(" ")
        print("***********************************")
        print(" Portfolio Name: {}".format(portfolio))
        print("***********************************")
        print(" ")

        # Load portfolio returns
        pf_returns = loader.load_portfolio_returns(freq, portfolio, log_returns=log_returns)

        merged = pd.merge(mktrf, pf_returns, on='date')

        y_data = merged.loc[:,'pfret'] - merged.loc[:,'rf']
        y_data = y_data.as_matrix().reshape(-1, 1)

        x_data = merged.iloc[:,1:-1]
        del x_data['rf']
        x_data = x_data.as_matrix()

        # Initialize the trainer
        trainer = Trainer(depth, width, no_lags+1)

        param = loader.load_portfolio_params(portfolio, freq, no_lags, depth, width)

        if param is None:
            trainer.run_ols_regression(x_data, y_data)
        else:
            trainer.load_parameters(param)

        # launch the learning
        params = trainer.train(x_data, y_data)

        loader.save_portfolio_params(params, name=portfolio, freq=freq, lags=no_lags, depth=depth, width=width)

        del trainer

    loader.close()

    return


# call the main function when called directly
if __name__ == "__main__":
    if len(sys.argv) == 4:
        freq = sys.argv[1]
        depth = int(sys.argv[2])
        width = int(sys.argv[3])
        train_portfolio_returns(freq, depth, width)

    elif len(sys.argv) == 5:
        freq = sys.argv[1]
        depth = int(sys.argv[2])
        width = int(sys.argv[3])
        portfolio_name = sys.argv[4]
        train_portfolio_returns(freq, depth, width, portfolio_name)

    else:
        train_portfolio_returns()

    print('** beep **\a')
