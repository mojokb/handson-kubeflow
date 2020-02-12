import os
import time

def train():
    print("Training...")
    import torch
    x = torch.Tensor(5, 3)
    print(x)
    time.sleep(1)

if __name__ == '__main__':
    if os.getenv('FAIRING_RUNTIME', None) is not None:
        train()
    else:
        from kubeflow import fairing
        DOCKER_REGISTRY = 'kubeflow-registry.default.svc.cluster.local:30000'
        file_name = os.path.basename(__file__)
        print("Executing {} remotely.".format(file_name))
        fairing.config.set_preprocessor('python', executable=file_name, input_files=[file_name])
        fairing.config.set_builder(
            'append', base_image='pytorch/pytorch:1.0-cuda10.0-cudnn7-devel',
            registry=DOCKER_REGISTRY, push=True)
        fairing.config.run()