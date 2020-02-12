import os
from kubeflow import fairing

DOCKER_REGISTRY = 'kubeflow-registry.default.svc.cluster.local:30000'
file_name = os.path.basename(__file__)
print("Executing {} remotely.".format(file_name))
fairing.config.set_preprocessor('notebook', notebook_file="test_notebook.ipynb")
fairing.config.set_builder('append',
                    base_image='pytorch/pytorch:1.0-cuda10.0-cudnn7-devel',
                    registry=DOCKER_REGISTRY, push=True)
fairing.config.run()