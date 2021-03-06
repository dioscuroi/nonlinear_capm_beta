import numpy as np

from Trainer import Trainer


def compute_beta(param, freq, no_lags):
    """compute_beta
    """

    # Prepare market excess returns as inputs
    if freq == 'daily':
        mktrf = np.arange(-3, 3 + 0.001, .1)

    elif freq == 'monthly':
        mktrf = np.arange(-20, 20 + 0.001, .2)

    x_data = np.zeros([len(mktrf), no_lags + 1])

    for i in range(0, no_lags + 1):
        x_data[:, i] = mktrf

    # Prepare Trainer
    trainer = Trainer()

    trainer.load_parameters(param)

    [_, beta] = trainer.derive_expret_beta(x_data)

    return beta[0]


def check_if_overfitted_by_param(param, freq, no_lags):
    """check_if_overfitted_by_param
    """

    beta = compute_beta(param, freq, no_lags)

    return check_if_overfitted_by_beta(beta)


def check_if_overfitted_by_beta(beta):
    """check_if_overfitted_by_beta
    """

    if beta is None:
        return True

    if np.any(np.isnan(beta)):
        return True

    beta0 = beta[:, 0]
    beta20 = np.sum(beta, axis=1)

    beta_average = np.mean(beta20)
    beta_stdev = np.std(beta20)

    # OLS is actually optimal for several stocks -- not sure now..
    if beta_stdev <= 1e-8:
        # return True
        return False

    normalized = (beta20 - beta_average) / beta_stdev

    if np.any(np.abs(normalized) > 4):
        return True

    return False


