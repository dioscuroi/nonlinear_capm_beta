import os.path
import numpy as np

from nonlinear_capm_beta.estimation import *


def plot_cum_beta(freq="monthly"):
    """plot_cum_beta
    """

    print("")
    print("***********************************")
    print(" plot_cum_beta() ")
    print(" freq: {}".format(freq))
    print("***********************************")

    if freq == "monthly":
        no_lags = 1
        mktrf = np.arange(-15, 15 + 0.001, .2)
    else:
        no_lags = 20
        mktrf = np.arange(-3, 3 + 0.001, .1)

    # Beta plot is drawn on the basis that RmRf is a vector of equal values
    x_data = np.zeros([no_lags + 1, len(mktrf)])

    for i in range(0, no_lags + 1):
        x_data[i] = mktrf

    # Prepare DataLoader and Trainer
    loader = DataLoader(connect=True)

    trainer = Trainer()

    # Iterate for portfolios
    print("")

    portfolio_list = ['size_lo', 'size_hi', 'value_lo', 'value_hi', 'smb', 'hml']

    for portfolio in portfolio_list:

        print("Portfolio: {}".format(portfolio))

        param = loader.load_portfolio_params(portfolio, freq, no_lags, depth=2, width=1)

        assert param is not None

        trainer.load_parameters(param)

        [_, beta] = trainer.derive_expret_beta(x_data.T)

        output_beta = np.zeros([len(mktrf), no_lags + 1])

        beta = beta[0]
        output_beta[:,0] = beta[:,0]

        for i in range(1, no_lags + 1):
            output_beta[:,i] = output_beta[:,i-1] + beta[:,i]

        filename = "outputs/plot_cum_beta_{}_{}.csv".format(freq, portfolio)

        output = np.concatenate((mktrf.reshape((-1,1)), output_beta), axis=1)

        np.savetxt(filename, output, fmt='%.4f', delimiter='\t')

    # Terminate
    loader.close()

if __name__ == "__main__":
    plot_cum_beta("daily")
    plot_cum_beta("monthly")

