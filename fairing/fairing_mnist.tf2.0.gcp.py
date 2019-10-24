import tensorflow as tf
import random
import os
from tensorflow.examples.tutorials.mnist import input_data


class MyModel(object):
    def train(self):
        mnist = tf.keras.datasets.mnist

        (x_train, y_train), (x_test, y_test) = mnist.load_data()
        x_train, x_test = x_train / 255.0, x_test / 255.0

        model = tf.keras.models.Sequential([
            tf.keras.layers.Flatten(input_shape=(28, 28)),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(10, activation='softmax')
        ])

        model.compile(optimizer='adam',
                      loss='sparse_categorical_crossentropy',
                      metrics=['accuracy'])

        model.fit(x_train, y_train, epochs=5)

        model.evaluate(x_test, y_test, verbose=2)


if __name__ == '__main__':
    if os.getenv('FAIRING_RUNTIME', None) is None:
        from kubeflow import fairing
        from kubeflow.fairing.kubernetes import utils as k8s_utils

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/jovyan/auth.json"
        GCP_PROJECT = fairing.cloud.gcp.guess_project_name()
        DOCKER_REGISTRY = 'gcr.io/{}/fairing-job'.format(GCP_PROJECT)
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
