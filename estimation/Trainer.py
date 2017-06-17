import os
import datetime
import numpy as np
import tensorflow as tf

class Trainer:
    """A simple class to run machine learning"""

    def __init__(self, depth=2, width=1, no_inputs=21, zero_init=True):
        """__init__
        """

        # if depth = 1, the model is identical to OLS regression
        assert(depth >= 1)

        # save the passed-over parameters
        self.depth = depth
        self.width = width
        self.no_inputs = no_inputs

        # generate weights
        self.weight = []
        self.bias   = []

        radius = 3

        if depth > 1:
            self.weight.append( np.random.rand(self.no_inputs, width) * (radius*2) - radius )

            for i in range(1,depth-1):
                self.weight.append( np.random.rand((width, width)) * (radius*2) - radius )

            self.weight.append( np.random.rand(width, 1) * (radius*3*2) - radius*3 )

        # generate biases
        for i in range(0, depth-1):
            self.bias.append( np.random.rand(1, width) * (radius*3*2) - radius*3 )

        self.bias.append( np.random.rand(1) * (radius*2) - radius )

        # if zero_init is True, set weights and biases to zeros
        if zero_init:
            for w in self.weight:
                w[:] = 0
            for b in self.bias:
                b[:] = 0

        # default linear-relation coefficients
        self.linear = np.zeros((no_inputs, 1))
        self.linear[0] = 1

        # output values to be saved after computation
        self.cost = None
        self.rmse = None
        self.sse = None
        self.r2 = None

    def run_ols_regression(self, x_data, y_data):
        """run_ols_regression
        """

        (no_obs, _) = x_data.shape

        one_vector = np.ones((no_obs, 1))

        temp = np.concatenate((one_vector, x_data), axis=1)

        temp1 = np.linalg.inv(np.dot(temp.T, temp))
        temp2 = np.dot(temp.T, y_data)

        beta = np.dot(temp1, temp2)

        self.linear = beta[1:]
        self.bias[-1][0] = beta[0]

    def load_parameters(self, param, add_noise=False):
        """load_parameters
        """

        self.weight[0] = np.array(param['weight0'])
        self.weight[1] = np.array(param['weight1'])
        self.bias[0] = np.array(param['bias0'])
        self.bias[1] = np.array(param['bias1'])
        self.linear = np.array(param['linear'])

        # add some noise
        if add_noise:
            print("adding noise..")

            for i in range(0, self.depth):
                (d1, d2) = self.weight[i].shape
                noise = np.random.rand(d1, d2) * .2 - .1
                self.weight[i] = self.weight[i] + noise

                d1 = len(self.bias[i])
                noise = np.random.rand(d1) * .2 - .1
                self.bias[i] = self.bias[i] + noise

    def build_a_tree(self):
        """build_a_tree
        """

        X = tf.placeholder(tf.float64, name='market_returns')

        w = []
        b = []

        for i in range(0,self.depth):
            w.append(tf.Variable(self.weight[i]))
            b.append(tf.Variable(self.bias[i]))

        if self.depth > 1:

            L = [ tf.sigmoid(tf.matmul(X, w[0]) + b[0]) ]

            for i in range(1, self.depth-1):

                L.append( tf.sigmoid(tf.matmul(L[i-1], w[i]) + b[i]) )

            L.append( tf.matmul(L[-1], w[-1]) + b[-1] )

        l = tf.Variable(self.linear)

        model = tf.matmul(X, l) + L[-1]

        return [X, model, w, b, l]

    def compute_sse(self, x_data, y_data):
        """compute_sse

        SSE: sum of squared errors
        """

        # define the model and SSE
        tf.reset_default_graph()

        Y = tf.placeholder(tf.float64, name='portfolio_returns')

        [X, model, tf_w, tf_b, tf_l] = self.build_a_tree()

        sse = tf.reduce_sum(tf.square(Y - model))

        init = tf.global_variables_initializer()

        sess = tf.Session()
        sess.run(init)

        result = sess.run(sse, feed_dict={X: x_data, Y: y_data})

        return result

    def train(self, x_data, y_data, max_total_steps=int(1e7) + 1, learning_rate=0.1, x_tolerance=1e-6, cost_tolerance=1e-6):
        """train
        """

        tf.reset_default_graph()

        # define a model and error terms
        Y = tf.placeholder(tf.float64, name='portfolio_returns')

        [X, model, tf_w, tf_b, tf_l] = self.build_a_tree()

        rmse = tf.sqrt(tf.reduce_mean(tf.square(Y - model)))
        cost = rmse

        # compute R2
        sse0 = tf.reduce_sum(tf.square(Y - tf.reduce_mean(Y)))
        sse1 = tf.reduce_sum(tf.square(Y - model))
        r2 = 1 - sse1 / sse0

        # placeholder for learning rate
        alpha = tf.placeholder(tf.float64, shape=[])

        # train = tf.train.GradientDescentOptimizer(learning_rate=alpha).minimize(cost)
        train = tf.train.AdamOptimizer(learning_rate=alpha).minimize(cost)

        # before starting, initialize the variables
        init = tf.global_variables_initializer()

        # launch
        sess = tf.Session()
        sess.run(init)

        # Let's create a checkpoint
        checkpoint_filename = "temp/checkpoint{}.tmp".format(os.getpid())

        saver = tf.train.Saver()
        saver.save(sess, checkpoint_filename)

        # compute the cost in the beginning
        prev_cost = sess.run(cost, feed_dict={X: x_data, Y: y_data})

        print("({})".format(datetime.datetime.now()))
        print("Beginning cost: {:.8f}, RMSE: {:.4f}, R2: {:.3f}".format(
            prev_cost,
            sess.run(rmse, feed_dict={X: x_data, Y: y_data}),
            sess.run(r2, feed_dict={X: x_data, Y: y_data})
        ))
        print("")

        # choose the first learning rate
        print("Looking for the learning rate to start with...")

        while learning_rate > x_tolerance:
            sess.run(train, feed_dict={X: x_data, Y: y_data, alpha: learning_rate})

            current_cost = sess.run(cost, feed_dict={X: x_data, Y: y_data})

            # learning rate is determined. Let's break the loop
            if current_cost < prev_cost:
                break

            # otherwise, cut the learning rate, restore the checkpoint, and repeat
            learning_rate = learning_rate / 2

            saver.restore(sess, checkpoint_filename)

        # quit the function if the parameter is already optimized
        if learning_rate < x_tolerance:
            print("The parameters are already optimized. No need to train anymore.")
            print("")

            self.cost = sess.run(cost, feed_dict={X: x_data, Y: y_data})
            self.rmse = sess.run(rmse, feed_dict={X: x_data, Y: y_data})
            self.sse = sess.run(sse1, feed_dict={X: x_data, Y: y_data})
            self.r2 = sess.run(r2, feed_dict={X: x_data, Y: y_data})

            return self.flush_params_to_dict()

        print("Training will start at the learning rate of {:4e}".format(learning_rate))


        for step in range(max_total_steps):
            sess.run(train, feed_dict={X: x_data, Y: y_data, alpha: learning_rate})

            if (step > 0) & (step % 1000 == 0):
                current_cost    = sess.run(cost, feed_dict={X: x_data, Y: y_data})

                print("Step: {:6d}, Cost: {:.8f}, RMSE: {:.4f}, R2: {:.3f}".format(
                    step, current_cost,
                    sess.run(rmse, feed_dict={X: x_data, Y: y_data}),
                    sess.run(r2, feed_dict={X: x_data, Y: y_data})
                ))

                # adjust learning rate if the result is not improved
                if (prev_cost - current_cost) < cost_tolerance:
                    learning_rate = learning_rate / 2

                    # print("({})".format(datetime.datetime.now()))
                    print("Learning rate is cut by two to {:.4e}".format(learning_rate))

                    # break the loop if learning rate is too small
                    if learning_rate < x_tolerance:
                        break

                # save the current state
                prev_cost = current_cost


        print("")
        print("Training is completed..")

        self.cost = sess.run(cost, feed_dict={X: x_data, Y: y_data})
        self.rmse = sess.run(rmse, feed_dict={X: x_data, Y: y_data})
        self.sse  = sess.run(sse1, feed_dict={X: x_data, Y: y_data})
        self.r2   = sess.run(r2,   feed_dict={X: x_data, Y: y_data})

        print("({})".format(datetime.datetime.now()))
        print("Cost in the end: {}, RMSE: {:.4f}, R2: {:.3f}".format(self.cost, self.rmse, self.r2))
        print("")

        for i in range(0, self.depth):
            self.weight[i] = sess.run(tf_w[i])
            self.bias[i]   = sess.run(tf_b[i])

        self.linear = sess.run(tf_l)

        return self.flush_params_to_dict()

    def flush_params_to_dict(self):
        """get_parameter_dict
        """

        params = dict()

        params['weight0'] = self.weight[0].tolist()
        params['weight1'] = self.weight[1].tolist()
        params['bias0'] = self.bias[0].tolist()
        params['bias1'] = self.bias[1].tolist()
        params['linear'] = self.linear.tolist()

        return params

    def derive_expret_beta(self, x_data):
        """derive_expret_beta
        """

        tf.reset_default_graph()

        [X, model, _, _, _] = self.build_a_tree()

        diff = tf.gradients(model, [X])

        init = tf.global_variables_initializer()

        sess = tf.Session()
        sess.run(init)

        expret = sess.run(model, feed_dict={X: x_data})
        beta   = sess.run(diff, feed_dict={X: x_data})

        return [expret, beta]
