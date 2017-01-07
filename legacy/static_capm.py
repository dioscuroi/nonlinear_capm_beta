import tensorflow as tf
import numpy as np

# data set
input = np.loadtxt('input.csv', unpack=True, dtype='float32')

[date, mktrf, smb, hml, rf, size1, size10, value1, value10] = input



beta = tf.Variable(1.)
alpha = tf.Variable(0.)

X = tf.placeholder(tf.float32)
Y = tf.placeholder(tf.float32)

capm = beta * X + alpha

# Simplified cost function
cost = tf.reduce_mean(tf.square(capm - Y))

# minimize
a = tf.Variable(0.01)  # learning rate, alpha
optimizer = tf.train.AdamOptimizer(a)
train = optimizer.minimize(cost)  # goal is minimize cost

# before starting, initialize the variables
init = tf.initialize_all_variables()

# launch
sess = tf.Session()
sess.run(init)

# fit the line
for step in range(1001):
    sess.run(train, feed_dict={X: mktrf, Y: size1})
    if step % 50 == 0:
        print( step, sess.run(cost, feed_dict={X: mktrf, Y: size1}), sess.run(beta), sess.run(alpha) )


diff = tf.gradients(capm, [X])

print( sess.run(diff, feed_dict={X: 0}) )