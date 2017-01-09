import os.path
import numpy as np

from nonlinear_capm_beta.estimation import *


def plot_expret_beta(freq="monthly"):

    if freq == "monthly":
        no_lags = 1
        mktrf = np.arange(-15, 15 + 0.001, .2)
        portfolio_list = ['small', 'large', 'growth', 'value']
    else:
        no_lags = 20
        mktrf = np.arange(-3, 3 + 0.001, .1)
        portfolio_list = ['small', 'large', 'growth', 'value', 'smb', 'hml']

    no_portfolios = len(portfolio_list)

    print("***********************************")
    print(" plot_expret_beta ")
    print(" freq: {}".format(freq))
    print("***********************************")

    # Beta plot is drawn on the basis that RmRf is a vector of equal values
    x_data = np.zeros([len(mktrf), no_lags + 1])

    for i in range(0, no_lags + 1):
        x_data[:,i] = mktrf

    # Template to save outputs
    output_expret = np.zeros([len(mktrf), no_portfolios])
    output_beta   = np.zeros([len(mktrf), no_portfolios])

    # Prepare DataLoader and Trainer
    loader = DataLoader(connect=True)

    trainer = Trainer()

    print("")

    # iterate for portfolios
    for portfolio_id in range(no_portfolios):

        portfolio = portfolio_list[portfolio_id]

        print("Portfolio: {}".format(portfolio))

        param = loader.load_portfolio_params(portfolio, freq, no_lags, depth=2, width=1)

        assert param is not None

        trainer.load_parameters(param)

        [expret, beta] = trainer.derive_expret_beta(x_data)

        output_expret[:,portfolio_id] = expret.reshape(-1)

        beta = beta[0]

        for i in range(0, no_lags + 1):
            output_beta[:,portfolio_id] += beta[:,i]

    for i in range(0, int(no_portfolios/2)):
        output = np.zeros([len(mktrf), 5])
        output[:,0] = mktrf
        output[:,1] = output_expret[:,i * 2]
        output[:,2] = output_expret[:,i * 2 + 1]
        output[:,3] = output_beta[:,i * 2]
        output[:,4] = output_beta[:,i * 2 + 1]

        filename = "outputs/plot_expret_beta_{}.csv".format(i)

        np.savetxt(filename, output, fmt='%.4f', delimiter='\t')

    # Terminate
    loader.close()

if __name__ == "__main__":
    plot_expret_beta("monthly")
