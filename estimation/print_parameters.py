import os
import pickle
import math
import numpy as np

def print_parameters(weight, bias, linear):
    depth = len(weight)
    (_, width) = weight[0].shape

    for i in range(0, depth):
        print("depth: {}".format(i))
        print(weight[i])
        print(bias[i])
        print("")

    print("linear terms")
    print(linear)
    print("")

    # Find where kinks are made
    beta_sum = np.sum(weight[0], axis=0)
    kink10 = - np.divide(bias[0] + math.log(1 / 0.10 - 1), beta_sum)
    kink50 = - np.divide(bias[0], beta_sum)
    kink90 = - np.divide(bias[0] + math.log(1 / 0.90 - 1), beta_sum)

    print("RmRf kinks (10 pctile, 50 pctile, 90 pctile)")
    print(kink10)
    print(kink50)
    print(kink90)
    print("")

    # Resulting values at kinks
    print("Resulting adjustments at kinks")
    print("- at 10 pctiles")

    temp = np.dot(np.ones((width, width)), 0.5)

    for i in range(0, width):
        temp[i,i] = 0.1

    print(np.dot(temp, weight[-1]) + bias[-1])

    print("- at median")

    temp = np.dot(np.ones((1, width)), 0.5)
    print(np.dot(temp, weight[-1]) + bias[-1])

    print("- at 90 pctiles")

    temp = np.dot(np.ones((width, width)), 0.5)

    for i in range(0, width):
        temp[i,i] = 0.9

    print(np.dot(temp, weight[-1]) + bias[-1])

    print("")





# initial parameters
# subfolder = "monthly_d2w2"
subfolder = "daily_d2w1"
# subfolder = "daily_d3w2"

print("***********************************")
print(" subfolder: {}".format(subfolder))
print("***********************************")

# for portfolio_id in range(0, 12):
for portfolio_id in [6]:

    filename = "{}/params_portfolio{}.dat".format(subfolder, portfolio_id)

    if not os.path.isfile(filename):
        break

    with open(filename, "rb") as f:
        data = pickle.load(f)

    print("***********************************")
    print(" Portfolio ID: {}".format(portfolio_id))
    print(" depth: {}, width: {}, no_inputs: {}".format(data.depth, data.width, data.no_inputs))
    print("***********************************")

    print_parameters(data.weight, data.bias, data.linear)


    # if need to change some parameters, add here
    # if portfolio_id == 6:
    if False:
        print("Changing some parameters..")

        print_parameters(data.weight, data.bias, data.linear)

        with open(filename, "wb") as f:
            pickle.dump(data, f)

