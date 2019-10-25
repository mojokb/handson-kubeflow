import tensorflow as tf
import random
import os
import argparse
from tensorflow.examples.tutorials.mnist import input_data


class MyModel(object):
    def train(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--learning_rate', required=False, type=float, default=0.01)
        parser.add_argument('--dropout_rate', required=False, type=float, default=0.2)
        args = parser.parse_args()

        mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
        learning_rate = args.learning_rate
        print("### learning_rate : ", learning_rate)
        training_epochs = 5
        batch_size = 100

        X = tf.placeholder(tf.float32, [None, 784])
        Y = tf.placeholder(tf.float32, [None, 10])

        keep_prob = tf.placeholder(tf.float32)

        W1 = tf.get_variable("W1", shape=[784, 512],
                             initializer=tf.contrib.layers.xavier_initializer())
        b1 = tf.Variable(tf.random_normal([512]))
        L1 = tf.nn.relu(tf.matmul(X, W1) + b1)
        L1 = tf.nn.dropout(L1, keep_prob=keep_prob)

        W2 = tf.get_variable("W3", shape=[512, 10],
                             initializer=tf.contrib.layers.xavier_initializer())
        b2 = tf.Variable(tf.random_normal([10]))

        hypothesis = tf.matmul(L1, W2) + b2

        cost = tf.reduce_mean(
            tf.nn.softmax_cross_entropy_with_logits(logits=hypothesis,
                                                    labels=Y))
        optimizer = tf.train.AdamOptimizer(
            learning_rate=learning_rate).minimize(cost)

        sess = tf.Session()
        sess.run(tf.global_variables_initializer())

        # train my model
        for epoch in range(training_epochs):
            avg_cost = 0
            total_batch = int(mnist.train.num_examples / batch_size)

            for i in range(total_batch):
                batch_xs, batch_ys = mnist.train.next_batch(batch_size)
                # keep_prob : Network의 70%를 유지해 학습
                feed_dict = {X: batch_xs, Y: batch_ys, keep_prob: args.dropout_rate}
                c, _ = sess.run([cost, optimizer], feed_dict=feed_dict)
                avg_cost += c / total_batch

            print('Epoch:', '%04d' % (epoch + 1), 'cost =',
                  '{:.9f}'.format(avg_cost))

            correct_prediction = tf.equal(tf.argmax(hypothesis, 1), tf.argmax(Y, 1))
            accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
            # Validation-accuracy
            print('Validation-accuracy=' + str(sess.run(accuracy, feed_dict={X: mnist.test.images,
                                                             Y: mnist.test.labels,
                                                             keep_prob: 1})))

        print('Learning Finished!')

        '''
        correct_prediction = tf.equal(tf.argmax(hypothesis, 1), tf.argmax(Y, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

        print('Accuracy:', sess.run(accuracy, feed_dict={X: mnist.test.images,
                                                         Y: mnist.test.labels,
                                                         keep_prob: 1}))

        for epoch in range(5):
            r = random.randint(0, mnist.test.num_examples - 1)
            # print("Test Random Label: ", sess.run(tf.argmax(mnist.test.labels[r:r + 1], 1)))
            print("\nTest Image -> ",
                  sess.run(tf.argmax(mnist.test.labels[r:r + 1], 1)))
            # plt.imshow(mnist.test.images[r:r + 1].reshape(28, 28), cmap='Greys', interpolation='nearest')
            # plt.show()
            print("Prediction: ", sess.run(tf.argmax(hypothesis, 1), feed_dict={
                X: mnist.test.images[r:r + 1], keep_prob: 1}))
        '''

if __name__ == '__main__':
    if os.getenv('FAIRING_RUNTIME', None) is None:
        from kubeflow import fairing
        from kubeflow.fairing.kubernetes import utils as k8s_utils

        DOCKER_REGISTRY = 'brightfly/fairing-job'
        fairing.config.set_builder(
            'append',
            base_image='gcr.io/kubeflow-images-public/tensorflow-1.13.1-notebook-cpu:v0.5.0',
            registry=DOCKER_REGISTRY, push=True)
        # cpu 1, memory 1GiB
        fairing.config.set_deployer('job',
                                    pod_spec_mutators=[
                                        k8s_utils.get_resource_mutator(cpu=1,
                                                                       memory=1)]
                                    )
        fairing.config.set_preprocessor('python', input_files=[__file__])
        fairing.config.run()
    else:
        remote_train = MyModel()
        remote_train.train()
