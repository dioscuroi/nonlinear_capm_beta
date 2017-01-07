import os.path
import numpy as np
from Trainer import *

def plot_eret_beta(subfolder = "daily_d2w1"):

    prefix = subfolder[0:subfolder.index("_")]

    if prefix == "monthly":
        no_inputs = 2
        no_portfolios = 12
        RmRf = np.arange(-15, 15 + 0.001, .2)
    else:
        no_inputs = 21
        no_portfolios = 6
        RmRf = np.arange(-3, 3 + 0.001, .1)


    print("***********************************")
    print(" plot_eret_beta ")
    print(" subfolder: {}".format(subfolder))
    print("***********************************")

    trainer = Trainer()

    # prepare output templat
    x_data = np.zeros([no_inputs, len(RmRf)])

    for i in range(0, no_inputs):
        x_data[i] = RmRf

    output_expret = np.zeros([no_portfolios, len(RmRf)])
    output_beta   = np.zeros([no_portfolios, len(RmRf)])


    # iterate for portfolios
    for portfolio_id in range(0, no_portfolios):

        filename = "{}/params_portfolio{}.dat".format(subfolder, portfolio_id)

        if not os.path.isfile(filename):
            no_portfolios = portfolio_id
            break

        print("portfolio {}..".format(portfolio_id))

        trainer.load_parameters(subfolder, portfolio_id)

        [expret, beta] = trainer.derive_expret_beta(x_data.T)

        output_expret[portfolio_id] = expret.T

        beta = beta[0].T

        for i in range(0, no_inputs):
            output_beta[portfolio_id] = output_beta[portfolio_id] + beta[i]


    for i in range(0, int(no_portfolios/2)):
        output = np.zeros([5, len(RmRf)])
        output[0] = RmRf.T
        output[1] = output_expret[i * 2]
        output[2] = output_expret[i * 2 + 1]
        output[3] = output_beta[i * 2]
        output[4] = output_beta[i * 2 + 1]

        filename = subfolder + "/plot_eret_beta{}.csv".format(i)

        np.savetxt(filename, output.T, fmt='%.4f', delimiter='\t')


if __name__ == "__main__":
    plot_eret_beta()
