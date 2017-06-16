import sys
import json
import os.path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from nonlinear_capm_beta.estimation import *


def plot_cum_beta(filename, portfolio):
    """plot_cum_beta
    """

    print("")
    print("***********************************")
    print(" plot_cum_beta ")
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

        plot_cum_beta_helper(filename, portfolio, id, param)

    return


def plot_cum_beta_helper(filename, portfolio, id, param):

    plot_title = "{}_{}_{}".format(filename, portfolio, id)

    print("Processing {}".format(plot_title))

    # fix no_lags to 20 for the moment
    no_lags = 20

    # prepare the x-axis to draw beta
    if str.find(filename, 'daily') >= 0:
        mktrf = np.arange(-3, 3 + 0.001, .1)
    else:
        mktrf = np.arange(-20, 20 + 0.001, .2)

    # Beta plot is drawn on the basis that RmRf is a vector of equal values
    x_data = np.zeros([len(mktrf), no_lags + 1])

    for i in range(0, no_lags + 1):
        x_data[:,i] = mktrf

    # compute cumulative beta
    trainer = Trainer()

    trainer.load_parameters(param)

    [_, beta] = trainer.derive_expret_beta(x_data)

    output_beta = np.zeros([len(mktrf), no_lags + 1])

    beta = beta[0]
    output_beta[:,0] = beta[:,0]

    for i in range(1, no_lags + 1):
        output_beta[:,i] = output_beta[:,i-1] + beta[:,i]

    del trainer

    # draw the cumulative beta graph using pyplot
    plt.figure(figsize=(6,3))

    plt.plot(mktrf, output_beta[:,0], 'r.', label='cum.beta.0')
    plt.plot(mktrf, output_beta[:,5], 'g--', label='cum.beta.5')
    plt.plot(mktrf, output_beta[:,20], 'k-', label='cum.beta.20')

    # plt.title(plot_title)
    plt.legend(loc='upper center')

    if str.find(filename, 'value') >= 0:
        plt.yticks(np.arange(0.8,2.01,0.2))
    else:
        plt.yticks(np.arange(0.7,2.51,0.3))

    plt.savefig('outputs/plot_cum_beta_{}.png'.format(plot_title))
    plt.close()

    return


# Global variables
sql_loader = None

if __name__ == "__main__":

    sql_loader = DataLoader(connect=True)

    plot_cum_beta('portfolio_size_daily', 'd1')
    plot_cum_beta('portfolio_size_daily', 'd10')
    plot_cum_beta('portfolio_value_daily', 'd1')
    plot_cum_beta('portfolio_value_daily', 'd10')

    sql_loader.close()

