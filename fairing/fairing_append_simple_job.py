import os
import tensorflow as tf

from kubeflow import fairing
# Setting up google container repositories (GCR) for storing output containers
# You can use any docker container registry istead of GCR
DOCKER_REGISTRY = 'registry.zipsacoding.com'
fairing.config.set_builder(
    'append',
    base_image='gcr.io/kubeflow-images-public/tensorflow-2.0.0a0-notebook-gpu:v0.7.0',
    registry=DOCKER_REGISTRY,
    push=True)
fairing.config.set_deployer('job',
                            namespace='test')

def train():
    tf.print(tf.constant(os.environ['HOSTNAME']))

if __name__ == '__main__':
    print('local train()')
    train()
    print('remote train()')
    remote_train = fairing.config.fn(train)
    remote_train()
