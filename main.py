#Implementation written from scratch based on example: https://gist.github.com/vinhkhuc/e53a70f9e5c3f55852b0
#Additions and modifications will be made.

import tensorflow as tf
import numpy as np
from sklearn import datasets
from sklearn.model_selection import train_test_split

RANDOM_SEED = 1
tf.set_random_seed(RANDOM_SEED)


def initialize_weights(shape, std_dev):
    weights = tf.random_normal(shape, std_dev)
    return tf.Variable(weights)


def forward_prop(x, w1, w2):
    s = tf.tanh(tf.matmul(x, w1))
    o = tf.matmul(s, w2)
    return o


def get_data():
    iris = datasets.load_iris()
    data = iris["data"]
    targets = iris["target"]

    n, m = data.shape
    all_x = np.ones((n, m+1))   # Create a matrix of 1's with the same shape as the data plus a bias column
    all_x[:, 1:] = data        # Set all but the last column to the actual data

    num_labels = len(np.unique(targets))
    all_y = np.eye(num_labels)[targets]
    return train_test_split(all_x, all_y, test_size=0.33, random_state=RANDOM_SEED)


train_x, test_x, train_y, test_y = get_data()

x_size = train_x.shape[1]   # Number of input nodes: 4 features and 1 bias
h_size = 256                # Number of hidden nodes
y_size = train_y.shape[1]   # Number of outcomes (3 iris flowers)

x = tf.placeholder("float", shape=(None, x_size))
y = tf.placeholder("float", shape=(None, y_size))

w1 = initialize_weights(shape=(x_size, h_size), std_dev=0.1)
w2 = initialize_weights(shape=(h_size, y_size), std_dev=0.1)

o = forward_prop(x, w1, w2)
predict = tf.argmax(o, axis=1)

cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=o))
updates = tf.train.GradientDescentOptimizer(0.01).minimize(cost)

init = tf.global_variables_initializer()

with tf.Session() as sess:
    sess.run(init)

    for epoch in range(300):
        for i in range(len(train_x)):
            sess.run(updates, feed_dict={x: train_x[i: i + 1], y: train_y[i: i + 1]})

        train_accuracy = np.mean(np.argmax(train_y, axis=1) == sess.run(predict, feed_dict={x: train_x, y: train_y}))
        test_accuracy = np.mean(np.argmax(test_y, axis=1) == sess.run(predict, feed_dict={x: test_x, y: test_y}))

        print("Epoch = %d, train accuracy = %.2f%%, test accuracy = %.2f%%" % (epoch + 1, train_accuracy * 100, test_accuracy * 100))