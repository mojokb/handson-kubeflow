import os
import tensorflow as tf

from kubeflow import fairing
# Setting up google container repositories (GCR) for storing output containers
# You can use any docker container registry istead of GCR
DOCKER_REGISTRY = 'kubeflow-registry.default.svc.cluster.local:30000'
fairing.config.set_builder(
    'append',
    base_image='brightfly/kubeflow-jupyter-lab:tf2.0-cpu',
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
