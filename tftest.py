import tensorflow as tf
import numpy as np

import time

X = tf.placeholder(tf.float32)
y_ = tf.placeholder(tf.float32)

w1 = tf.Variable(tf.truncated_normal([2, 1]))
b1 = tf.Variable(tf.zeros([1]))

y = tf.matmul(X, w1) + b1
loss = (y - y_) ** 2 * .5

mean_loss = tf.reduce_mean(loss)
optimizer = tf.train.AdamOptimizer(1e-1 * 2).minimize(mean_loss)

def main():
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        for i in range (100):
            inp = np.random.random([1, 2]) * 5
            tar = np.sum(inp, axis = 1) * 2 + 1
            _, xloss, labels = sess.run([optimizer, mean_loss, y], feed_dict = {X: inp, y_:tar})
            print(xloss)

        for i in range (100):
            inp = np.random.random([1, 2]) * 5
            tar = np.sum(inp, axis = 1) * 2 + 1

            out = sess.run([y], feed_dict = {X : inp})
            print(tar[0], out[0][0])

        print (sess.run(w1))
        print (sess.run(b1))
main()
