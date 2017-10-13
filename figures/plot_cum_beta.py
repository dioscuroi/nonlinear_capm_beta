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

    # no_lags = 20 for daily returns, = 1 for monthly returns
    if str.find(filename, 'daily') >= 0:
        no_lags = 20
        mktrf = np.arange(-3, 3 + 0.001, .1)

    else:
        no_lags = 1
        mktrf = np.arange(-20, 20 + 0.001, 1)

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
    if no_lags >= 20:
        print("average cum.beta.0 : {:.4f}".format(np.mean(output_beta[:,0])))
        print("average cum.beta.5 : {:.4f}".format(np.mean(output_beta[:,5])))
        print("average cum.beta.20: {:.4f}".format(np.mean(output_beta[:,20])))

        plt.figure(figsize=(7, 3))

        plt.plot(mktrf, output_beta[:, 0], 'r.', label='cumulative beta over 0 day')
        plt.plot(mktrf, output_beta[:, 5], 'g--', label='cumulative beta over 5 days')
        plt.plot(mktrf, output_beta[:, 20], 'k-', label='cumulative beta over 20 days')

        if str.find(filename, 'value') >= 0:
            plt.yticks(np.arange(0.8, 2.01, 0.2))
        elif str.find(filename, 'size') >= 0:
            plt.yticks(np.arange(0.5, 2.51, 0.5))
        elif str.find(filename, 'ff3factors') >= 0:
            plt.yticks(np.arange(-.4, .61, 0.2))
    else:
        print("average cum.beta.0 : {:.4f}".format(np.mean(output_beta[:,0])))
        print("average cum.beta.1 : {:.4f}".format(np.mean(output_beta[:,1])))

        plt.figure(figsize=(3.5, 3))

        plt.plot(mktrf, output_beta[:, 0], 'r.', label='cumulative beta over 0 month')
        plt.plot(mktrf, output_beta[:, 1], 'k-', label='cumulative beta over 1 month')

        if str.find(filename, 'value') >= 0:
            plt.yticks(np.arange(0.5, 4.01, 0.5))
        elif str.find(filename, 'size') >= 0:
            plt.yticks(np.arange(0.5, 4.01, 0.5))
        elif str.find(filename, 'ff3factors') >= 0:
            plt.yticks(np.arange(-.4, .61, 0.2))

    # plt.title(plot_title)
    plt.legend(loc='upper center')
    plt.grid()
    plt.tight_layout()

    plt.savefig('outputs/plot_cum_beta_{}.png'.format(plot_title))
    plt.close()

    return


# Global variables
sql_loader = None

if __name__ == "__main__":

    sql_loader = DataLoader(connect=True)

    # plot_cum_beta('portfolio_size_daily', 'd1')
    # plot_cum_beta('portfolio_size_daily', 'd10')
    # plot_cum_beta('portfolio_value_daily', 'd1')
    # plot_cum_beta('portfolio_value_daily', 'd10')
    #
    # plot_cum_beta('ff3factors_daily', None)

    plot_cum_beta('portfolio_size', 'd1')
    plot_cum_beta('portfolio_size', 'd10')
    plot_cum_beta('portfolio_value', 'd1')
    plot_cum_beta('portfolio_value', 'd10')

    sql_loader.close()

