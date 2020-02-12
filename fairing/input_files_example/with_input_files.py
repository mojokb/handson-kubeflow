import os
import tensorflow as tf
from kubeflow import fairing

DOCKER_REGISTRY = 'kubeflow-registry.default.svc.cluster.local:30000'

fairing.config.set_builder('append',
                           base_image='tensorflow/tensorflow:1.14.0-py3',
                           registry=DOCKER_REGISTRY, push=True)
fairing.config.set_deployer('job')


def train():
    hostname = tf.constant(os.environ['HOSTNAME'])
    sess = tf.Session()
    print('Hostname: ', sess.run(hostname).decode('utf-8'))


if __name__ == '__main__':
    fairing.config.set_preprocessor('function',
                                    function_obj=train,
                                    input_files=["data.csv",
                                                 "requirements.txt"])
    fairing.config.run()
