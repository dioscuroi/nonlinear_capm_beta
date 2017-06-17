import sys
import json
import os.path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.stats import f

from nonlinear_capm_beta.estimation import *


def hypothesis_testing(filename, portfolio):
    """hypothesis_testing
    """

    print("")
    print("***********************************")
    print(" hypothesis_testing ")
    print(" filename: {}".format(filename))
    print(" portfolio: {}".format(portfolio))
    print("***********************************")
    print("")

    query = """
        select portfolio, id, parameters
        from beta_portfolios
        where filename = '{}'
    """.format(filename)

    if portfolio is not None:
        query = query + " and portfolio = '{}'".format(portfolio)

    df = sql_loader.sql_query_select(query)

    for i in range(len(df)):
        portfolio = df.loc[i, 'portfolio']
        id = df.loc[i, 'id']
        param = json.loads(df.loc[i, 'parameters'])

        hypothesis_testing_helper(filename, portfolio, id, param)

    return


def hypothesis_testing_helper(filename, portfolio, id, param):

    print("Processing {}_{}_{}".format(filename, portfolio, id))

    # Load data
    [x_data, y_data] = load_data(filename, portfolio, no_lags=20)

    no_obs = len(y_data)

    # Unrestricted SSE
    trainer = Trainer(depth=2, width=1, no_inputs=x_data.shape[1], zero_init=True)

    trainer.load_parameters(param)

    usse = trainer.compute_sse(x_data, y_data)

    print("")
    print("Unrestricted SSE: {:.2f}".format(usse))

    # Hypothesis 1: no convexity
    print("")
    print("* Hypothesis 1: no convexity")

    trainer = Trainer(depth=2, width=1, no_inputs=x_data.shape[1], zero_init=True)

    trainer.run_ols_regression(x_data, y_data)

    rsse1 = trainer.compute_sse(x_data, y_data)

    no_restrictions = len(param['weight0']) + len(param['weight1']) + len(param['bias0'])

    print_F_statistics(usse, rsse1, no_obs, no_restrictions)

    # Hypothesis 2: no delay
    print("")
    print("* Hypothesis 2: no delay")

    trainer = Trainer(depth=2, width=1, no_inputs=1, zero_init=True)

    xdata_without_lags = x_data[:, 0].reshape(-1,1)

    trainer.run_ols_regression(xdata_without_lags, y_data)

    param2 = trainer.train(xdata_without_lags, y_data)

    rsse2 = trainer.sse

    no_restrictions = count_no_restrictions(param, param2)

    print_F_statistics(usse, rsse2, no_obs, no_restrictions)

    # Hypothesis 3: no delay beyond 5 days
    print("")
    print("* Hypothesis 3: no delay beyond 5 days")

    trainer = Trainer(depth=2, width=1, no_inputs=6, zero_init=True)

    xdata_with_5lags = x_data[:, 0:6]

    trainer.run_ols_regression(xdata_with_5lags, y_data)

    param3 = trainer.train(xdata_with_5lags, y_data)

    rsse3 = trainer.sse

    no_restrictions = count_no_restrictions(param, param3)

    print_F_statistics(usse, rsse3, no_obs, no_restrictions)

    return


def count_no_restrictions(param_un, param_re):

    no_param_un = 0
    no_param_re = 0

    for item in param_un.values():
        no_param_un = no_param_un + len(item)

    for item in param_re.values():
        no_param_re = no_param_re + len(item)

    no_restrictions = no_param_un - no_param_re

    return no_restrictions


def print_F_statistics(usse, rsse, no_obs, no_restrictions):

    F_num = (rsse - usse) / no_restrictions
    F_den = usse / (no_obs - no_restrictions)
    F = F_num / F_den
    pval = 1 - f.cdf(F, no_restrictions, no_obs - no_restrictions)

    print("Restricted SSE: {:.2f}".format(rsse))
    print("F-stat: {:.3f}".format(F))
    print("p-value: {:.2e}".format(pval))

    return


def load_data(filename, portfolio, no_lags):

    # Load market returns
    if str.find(filename, 'daily') >= 0:
        mktrf = pd.read_stata(data_path + 'ff3factors_daily.dta')
    else:
        mktrf = pd.read_stata(data_path + 'ff3factors_monthly.dta')

    mktrf = mktrf[['date', 'mktrf', 'rf']]

    # Generate lagged returns
    for i in range(no_lags):
        mktrf['L{}.mktrf'.format(i + 1)] = mktrf['mktrf'].shift(i + 1)

    idx_missing = np.isnan(mktrf[mktrf.columns[-1]])

    mktrf = mktrf.loc[~idx_missing]

    # Load portfolio returns
    pf_returns = pd.read_stata(data_path + filename + '.dta')
    pf_returns = pf_returns[['date', portfolio]]

    # Merge the two datasets
    merged = pd.merge(pf_returns, mktrf, on='date')

    # Generate X and Y data in numpy formats
    if (portfolio == 'smb') or (portfolio == 'hml'):
        y_data = merged.loc[:, portfolio]
    else:
        y_data = merged.loc[:, portfolio] - merged.loc[:, 'rf']

    y_data = y_data.as_matrix().reshape(-1, 1)

    x_data = merged.iloc[:, 2:]
    del x_data['rf']
    x_data = x_data.as_matrix()

    return [x_data, y_data]


# Global variables
sql_loader = None

data_path = '/Users/dioscuroi/OneDrive - UNSW/Research Data/Stocks/Fama_French/'

if __name__ == "__main__":

    sql_loader = DataLoader(connect=True)

    hypothesis_testing('portfolio_size_daily', 'd1')
    hypothesis_testing('portfolio_size_daily', 'd10')
    hypothesis_testing('portfolio_value_daily', 'd1')
    hypothesis_testing('portfolio_value_daily', 'd10')

    sql_loader.close()

