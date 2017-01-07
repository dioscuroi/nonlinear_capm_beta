import sys
import os.path
from Trainer import *
from plot_cum_beta import plot_cum_beta
from plot_eret_beta import plot_eret_beta

def dynamic_capm(subfolder_prefix="monthly", depth=2, width=1, portfolio_id = None):

    # load data set
    # input - date, current and lagged market returns
    # output - date, portfolio returns
    input_file  = "{}_input.csv".format(subfolder_prefix)
    output_file = "{}_output.csv".format(subfolder_prefix)

    input  = np.loadtxt(input_file , unpack=True, dtype='float64')
    output = np.loadtxt(output_file, unpack=True, dtype='float64')

    mktrf = input[1:]
    portfolio_returns = output[1:]

    (no_inputs,_) = mktrf.shape
    (no_portfolios,_) = portfolio_returns.shape

    print("***********************************")
    print(" Dynamic CAPM")
    print(" prefix: {}".format(subfolder_prefix))
    print(" depth: {}, width: {}".format(depth, width))
    print(" no_inputs: {}, no_portfolios: {}".format(no_inputs, no_portfolios))
    print("***********************************")


    # setup a working directory
    subfolder = "{}_d{}w{}".format(subfolder_prefix, depth, width)

    if not os.path.exists(subfolder):
        os.mkdir(subfolder)


    # now run the machine learning on portfolio returns
    if portfolio_id is None:
        portfolio_list = range(0, no_portfolios)
    else:
        portfolio_list = [portfolio_id]

    for portfolio_id in portfolio_list:

        print(" ")
        print("***********************************")
        print(" Portfolio ID: {}".format(portfolio_id))
        print("***********************************")
        print(" ")

        # choose portfolio return data
        y_data = portfolio_returns[portfolio_id]

        index = np.where(y_data > -999)

        y_data = y_data[index].reshape(-1,1)
        x_data = mktrf.T[index, :].reshape(-1, no_inputs)

        # initialize the trainer
        trainer = Trainer(depth, width, no_inputs)

        trainer.run_ols_regression(x_data, y_data)

        trainer.load_parameters(subfolder, portfolio_id, add_noise=False)

        # launch the learning
        trainer.train(x_data, y_data)

        del trainer

        plot_cum_beta(subfolder, portfolio_id)


    if len(portfolio_list) > 1:
        plot_eret_beta(subfolder)



# call the main function when called directly
if __name__ == "__main__":
    if len(sys.argv) == 4:
        depth = int(sys.argv[2])
        width = int(sys.argv[3])
        dynamic_capm(sys.argv[1], depth, width)

    elif len(sys.argv) == 5:
        depth = int(sys.argv[2])
        width = int(sys.argv[3])
        portfolio_id = int(sys.argv[4])
        dynamic_capm(sys.argv[1], depth, width, portfolio_id)

    else:
        dynamic_capm()

    print('** beep **\a')
