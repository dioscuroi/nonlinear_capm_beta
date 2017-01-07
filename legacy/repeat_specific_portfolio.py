import os
import sys
import shutil
import gc
from dynamic_capm import dynamic_capm

def repeat_specific_portfolio(prefix = "monthly", depth = 2, width = 1, portfolio_id = 6):

    # setup a working directory
    subfolder = "{}_d{}w{}".format(prefix, depth, width)

    no_repeats = 50

    for repeat_id in range(0, no_repeats):

        dest = "{}/params_portfolio{}_{}.dat".format(subfolder, portfolio_id, repeat_id)

        if os.path.isfile(dest):
            continue

        print("")
        print("==== Repeat ID: {} ====".format(repeat_id))
        print("")

        dynamic_capm(prefix, depth, width, portfolio_id)

        source = "{}/params_portfolio{}.dat".format(subfolder, portfolio_id)
        dest   = "{}/params_portfolio{}_{}.dat".format(subfolder, portfolio_id, repeat_id)

        shutil.move(source, dest)

        source = "{}/plot_cum_beta{:2d}.csv".format(subfolder, portfolio_id)
        dest   = "{}/plot_cum_beta{:2d}_{}.csv".format(subfolder, portfolio_id, repeat_id)

        shutil.move(source, dest)

        gc.collect()


# call the main function when called directly
if __name__ == "__main__":
    if len(sys.argv) == 5:

        depth = int(sys.argv[2])
        width = int(sys.argv[3])
        portfolio_id = int(sys.argv[4])

        repeat_specific_portfolio(sys.argv[1], depth, width, portfolio_id)

    else:
        repeat_specific_portfolio()