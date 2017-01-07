import os.path
import numpy as np
from Trainer import *


def plot_cum_beta(subfolder = "daily_d2w1", portfolio_id = 0):
    print("***********************************")
    print(" plot_cum_beta() ")
    print(" subfolder: {}".format(subfolder))
    print("***********************************")

    prefix = subfolder[0:subfolder.index("_")]

    if prefix == "monthly":
        no_inputs = 2
        no_portfolios = 15
        RmRf = np.arange(-15, 15 + 0.001, .2)
    else:
        no_inputs = 21
        no_portfolios = 9
        RmRf = np.arange(-3, 3 + 0.001, .1)


    trainer = Trainer()

    # prepare output templat
    x_data = np.zeros([no_inputs, len(RmRf)])

    for i in range(0, no_inputs):
        x_data[i] = RmRf


    # iterate for portfolios
    if portfolio_id is None:
        portfolio_list = range(0, no_portfolios)
    else:
        portfolio_list = [portfolio_id]

    for portfolio_id in portfolio_list:

        print("portfolio {}..".format(portfolio_id))

        filename = "{}/params_portfolio{}.dat".format(subfolder, portfolio_id)

        if not os.path.isfile(filename):
            no_portfolios = portfolio_id
            break

        trainer.load_parameters(subfolder, portfolio_id)

        [_, beta] = trainer.derive_expret_beta(x_data.T)

        output_beta = np.zeros([no_inputs, len(RmRf)])

        beta = beta[0].T
        output_beta[0] = beta[0]

        for i in range(1, no_inputs):
            output_beta[i] = output_beta[i-1] + beta[i]

        filename = subfolder + "/plot_cum_beta{:2d}.csv".format(portfolio_id)

        output = np.concatenate((RmRf.reshape((1,-1)), output_beta))

        np.savetxt(filename, output.T, fmt='%.4f', delimiter='\t')



if __name__ == "__main__":
    plot_cum_beta()

