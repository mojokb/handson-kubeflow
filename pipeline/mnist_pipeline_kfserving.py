import kfp
import kfp.dsl as dsl

def echo_op(text):
    return dsl.ContainerOp(
        name='echo',
        image='library/bash:4.4.23',
        command=['sh', '-c'],
        arguments=['echo "$0"', text],
    )

@dsl.pipeline(
    name='MnistPipeline',
    description='mnist '
)
def mnist_pipeline(volume_size, learning_rate, dropout_rate, checkpoint_dir,
                   saved_model_dir, tensorboard_log, namespace, storage_uri,
                   name):
    exit_task = echo_op("Done!")
    with dsl.ExitHandler(exit_task):
        vop = dsl.VolumeOp(
            name='mnist_model',
            resource_name='mnist_model',
            storage_class="nfs-client",
            modes=dsl.VOLUME_MODE_RWM,
            size=volume_size
        )

        mnist = dsl.ContainerOp(
            name='Mnist',
            image='kubeflow-registry.default.svc.cluster.local:30000/katib-job:FF61F3B',
            command=['python', '/app/Untitled.py'],
            arguments=[
                "--learning_rate", learning_rate,
                "--dropout_rate", dropout_rate,
                "--checkpoint_dir", checkpoint_dir,
                "--saved_model_dir", saved_model_dir,
                "--tensorboard_log", tensorboard_log
            ],
            pvolumes={"/result": vop.volume}
        )

        result = dsl.ContainerOp(
            name='list_list',
            image='library/bash:4.4.23',
            command=['ls', '-R', '/result'],
            pvolumes={"/result": mnist.pvolume}
        )
        kfserving = dsl.ContainerOp(
            name='kfserving',
            image='kubeflow-registry.default.svc.cluster.local:30000/kfserving:6D7B836C',
            command=['python', '/app/kfserving-fairing.py'],
            arguments=[
                "--namespace", namespace,
                "--storage_uri", "pvc://" + str(vop.volume.persistent_volume_claim.claim_name) + str(storage_uri),
                "--name", name
            ],
            pvolumes={"/result": mnist.pvolume}
        )
        mnist.after(vop)
        result.after(mnist)
        kfserving.after(mnist)
        kfserving.after(vop)

arguments = {'volume_size' : '5Gi',
             'learning_rate': '0.01',
             'dropout_rate': '0.2',
             'checkpoint_dir': '/result/training_checkpoints',
             'saved_model_dir': '/result/saved_model/0001',
             'tensorboard_log': '/result/log',
             'namespace': 'kubeflow',
             'storage_uri': '/saved_model',
             'name': 'kfserving-mnist-01'
             }

if __name__ == '__main__':
    kfp.Client().create_run_from_pipeline_func(pipeline_func=mnist_pipeline,
                                               arguments=arguments)
