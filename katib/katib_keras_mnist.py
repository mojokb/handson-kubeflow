import os
import tensorflow as tf
import argparse
from tensorflow.python.keras.callbacks import Callback


class MyModel(object):
    def train(self):
        mnist = tf.keras.datasets.mnist

        # 입력 값을 받게 추가합니다.
        parser = argparse.ArgumentParser()
        parser.add_argument('--learning_rate', required=False, type=float, default=0.01)
        parser.add_argument('--dropout_rate', required=False, type=float, default=0.2)
        args = parser.parse_args()

        (x_train, y_train), (x_test, y_test) = mnist.load_data()
        x_train, x_test = x_train / 255.0, x_test / 255.0

        model = tf.keras.models.Sequential([
            tf.keras.layers.Flatten(input_shape=(28, 28)),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(args.dropout_rate),
            tf.keras.layers.Dense(10, activation='softmax')
        ])

        sgd = tf.keras.optimizers.SGD(lr=args.learning_rate,
                                      decay=1e-6,
                                      momentum=0.9,
                                      nesterov=True)

        model.compile(optimizer=sgd,
                      loss='sparse_categorical_crossentropy',
                      metrics=['acc'])

        model.fit(x_train, y_train,
                  verbose=0,
                  validation_data=(x_test, y_test),
                  epochs=5,
                  callbacks=[KatibMetricLog()])


class KatibMetricLog(Callback):
    def on_batch_end(self, batch, logs={}):
        print("batch", str(batch),
              "accuracy=" + str(logs.get('acc')),
              "loss=" + str(logs.get('loss')))

    def on_epoch_begin(self, epoch, logs={}):
        print("epoch " + str(epoch) + ":")

    def on_epoch_end(self, epoch, logs={}):
        print("Validation-accuracy=" + str(logs.get('val_acc')),
              "Validation-loss=" + str(logs.get('val_loss')))
        return


if __name__ == '__main__':
    if os.getenv('FAIRING_RUNTIME', None) is None:
        from kubeflow import fairing
        from kubeflow.fairing.kubernetes import utils as k8s_utils

        DOCKER_REGISTRY = 'kubeflow-registry.default.svc.cluster.local:30000'
        fairing.config.set_builder(
            'append',
            image_name='katib-job',
            base_image='brightfly/kubeflow-jupyter-lab:tf2.0-gpu',
            registry=DOCKER_REGISTRY,
            push=True)
        # cpu 1, memory 1GiB
        fairing.config.set_deployer('job',
                                    namespace='amaramusic'
                                    )
        # python3
        #fairing.config.set_preprocessor('python', input_files=[__file__])
        fairing.config.run()
    else:
        remote_train = MyModel()
        remote_train.train()
