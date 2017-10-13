import sys
import json
import numpy as np
import pandas as pd

from datetime import date, datetime

from utils import *
from Trainer import Trainer
from DataLoader import DataLoader
from nonlinear_capm_beta.figures.plot_cum_beta import plot_cum_beta


def train_portfolio_returns(filename, portfolio, no_lags, zero_init=True):

    print("*************************************************")
    print(" Train Portfolio Returns")
    print(" ")
    print(" filename: {}".format(filename))
    print(" portfolio: {}".format(portfolio))
    print(" no_lags: {}".format(no_lags))
    print("*************************************************")


    # Load portfolio and market returns
    data_path = '/Users/dioscuroi/OneDrive - UNSW/Research Data/Stocks/Fama_French/'

    df_portfolios = pd.read_stata(data_path + filename + '.dta')

    if str.find(filename, 'daily') >= 0:
        df_markets = pd.read_stata(data_path + 'ff3factors_daily.dta')
    else:
        df_markets = pd.read_stata(data_path + 'ff3factors_monthly.dta')

    df_markets = df_markets[['date', 'mktrf', 'rf']]

    # Generate lagged returns
    for i in range(no_lags):
        df_markets['L{}.mktrf'.format(i + 1)] = df_markets['mktrf'].shift(i + 1)

    idx_missing = np.isnan(df_markets[df_markets.columns[-1]])

    df_markets = df_markets.loc[~idx_missing]

    # Iterate for portfolios
    if portfolio is None:
        for col in df_portfolios.columns[1:]:
            train_portfolio_helper(filename, df_portfolios[['date', col]], df_markets, zero_init)

    else:
        train_portfolio_helper(filename, df_portfolios[['date', portfolio]], df_markets, zero_init)

    return


def train_portfolio_helper(filename, pf_returns, mktrf, zero_init):

    # drop missing returns
    idx_missing = (pf_returns.iloc[:, 1] < -99)

    pf_returns = pf_returns.loc[~idx_missing]

    merged = pd.merge(pf_returns, mktrf, on='date')

    # Retrieve portfolio info and print
    pf_name = pf_returns.columns[1]
    no_obs = len(merged)
    no_lags = len(mktrf.columns) - 3

    # return if the number of observations is not sufficient enough
    if no_obs < (no_lags + 1) * 2:
        return

    print("")
    print("*************************************************")
    print("({})".format(datetime.today()))
    print("portfolio: {}".format(pf_name))
    print("no_obs: {}".format(no_obs))
    print("*************************************************")

    if (pf_name == 'smb') or (pf_name == 'hml'):
        y_data = merged.loc[:, pf_name]
    else:
        y_data = merged.loc[:, pf_name] - merged.loc[:, 'rf']

    y_data = y_data.as_matrix().reshape(-1, 1)

    x_data = merged.iloc[:, 2:]
    del x_data['rf']
    x_data = x_data.as_matrix()

    # Initialize the trainer
    max_retries = 5

    for attempt_id in range(max_retries):

        trainer = Trainer(depth=2, width=1, no_inputs=x_data.shape[1], zero_init=zero_init)

        trainer.run_ols_regression(x_data, y_data)

        params = trainer.train(x_data, y_data, x_tolerance=1e-6, cost_tolerance=1e-6)

        del trainer

        if not check_if_overfitted_by_param(params, freq="daily", no_lags=no_lags):
            break

        params = None
        zero_init = False

        print("Parameters are overfitted. Let's try again.")
        print("")

    # if parameters are still overfitted, replace parameters with OLS coefficients
    if params is None:
        trainer = Trainer(depth=2, width=1, no_inputs=x_data.shape[1], zero_init=True)
        trainer.run_ols_regression(x_data, y_data)
        params = trainer.flush_params_to_dict()

    # compute beta
    if str.find(filename, 'daily') >= 0:
        freq = 'daily'
    else:
        freq = 'monthly'

    beta = compute_beta(param=params, freq=freq, no_lags=no_lags)

    assert (not check_if_overfitted_by_beta(beta))

    beta0 = beta[:, 0]
    beta20 = np.sum(beta, axis=1)

    beta_average = np.mean(beta20)
    beta_delay = np.mean(beta20) - np.mean(beta0)
    beta_convexity = (beta20[0] + beta20[-1]) / 2 - beta20[int((len(beta20) - 1) / 2)]

    # Save the results to SQL server
    sql_loader = DataLoader(connect=True)

    query = """
        select max(id)
        from beta_portfolios
        where filename = '{}' and portfolio = '{}' and lags = {}
    """.format(filename, pf_name, no_lags)

    max_id = sql_loader.sql_query_select(query)

    if max_id.iloc[0,0] is None:
        next_id = 1
    else:
        next_id = max_id.iloc[0,0] + 1

    query = """
      insert into beta_portfolios
      VALUES
      ('{}', '{}', {}, {}, {}, now(), '{}', {}, {}, {})
    """.format(filename, pf_name, no_lags, next_id, no_obs,
               json.dumps(params), beta_average, beta_delay, beta_convexity)

    sql_loader.sql_query_commit(query)

    print("Results:")
    print(" - filename: {}, portfolio: {}".format(filename, pf_name))
    print(" - beta_average: {:.3f}, beta_delay: {:.3f}, beta_convexity: {:.3f}".format(
        beta_average, beta_delay, beta_convexity))
    print("")

    sql_loader.close()

    return


# call the main function when called directly
if __name__ == "__main__":

    # # default parameters
    # filename = 'portfolio_size_daily'
    # portfolio = None
    # no_lags = 20
    #
    # # parse parameters passed over from the command line
    # if len(sys.argv) >= 2:
    #     filename = sys.argv[1]
    #
    # if len(sys.argv) >= 3:
    #     portfolio = sys.argv[2]
    #
    # if len(sys.argv) >= 4:
    #     no_lags = int(sys.argv[3])
    #
    # # Estimate beta parameters
    # train_portfolio_returns(filename, portfolio, no_lags)

    # train_portfolio_returns('portfolio_size_daily', 'd1', 20)
    # train_portfolio_returns('portfolio_size_daily', 'd10', 20)
    # train_portfolio_returns('portfolio_value_daily', 'd1', 20)
    # train_portfolio_returns('portfolio_value_daily', 'd10', 20)

    # train_portfolio_returns('ff3factors_daily', 'smb', 20)
    # train_portfolio_returns('ff3factors_daily', 'hml', 20)

    train_portfolio_returns('portfolio_size', 'd1', 1)
    train_portfolio_returns('portfolio_size', 'd10', 1)
    train_portfolio_returns('portfolio_value', 'd1', 1)
    train_portfolio_returns('portfolio_value', 'd10', 1)

    # Terminate
    print('** beep **\a')
