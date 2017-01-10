import numpy as np

from Trainer import Trainer


def compute_beta(param, freq='daily'):
    """compute_beta
    """

    # Prepare market excess returns as inputs
    if freq == 'daily':
        no_lags = 20
        mktrf = np.arange(-3, 3 + 0.001, .1)

    elif freq == 'monthly':
        no_lags = 1
        mktrf = np.arange(-20, 20 + 0.001, .2)

    x_data = np.zeros([len(mktrf), no_lags + 1])

    for i in range(0, no_lags + 1):
        x_data[:, i] = mktrf

    # Prepare Trainer
    trainer = Trainer()

    trainer.load_parameters(param)

    [_, beta] = trainer.derive_expret_beta(x_data)

    return beta[0]


def check_if_overfitted_by_param(param, freq='daily'):
    """check_if_overfitted_by_param
    """

    beta = compute_beta(param, freq)

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

    if beta_stdev <= 1e-4:
        return True

    normalized = (beta20 - beta_average) / beta_stdev

    if np.any(np.abs(normalized) > 3):
        return True

    return False


