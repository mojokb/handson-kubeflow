import kfp
import kfp.dsl as dsl
import kfp.onprem as onprem

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
def mnist_pipeline(learning_rate, dropout_rate, checkpoint_dir, saved_model_dir, tensorboard_log):
    exit_task = echo_op("Done!")
    with dsl.ExitHandler(exit_task):    
        vop = dsl.VolumeOp(
            name="mnist_model_volume",
            resource_name="mnist_model",
            storage_class="nfs-client",
            modes=dsl.VOLUME_MODE_RWM,
            size="10Gi"
        )
        
        mnist = dsl.ContainerOp(
            name='Mnist',
            image='kubeflow-registry.default.svc.cluster.local:30000/katib-job:2B27615F',
            command=['python', '/app/mnist_to_pipeline.py'],
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

        mnist.after(vop)
        result.after(mnist)
    

arguments = {'learning_rate': '0.01',
             'dropout_rate': '0.2',
             'checkpoint_dir': '/reuslt/training_checkpoints',
             'saved_model_dir':'/result/saved_model',
             'tensorboard_log': '/result/log' 
            }
    
if __name__ == '__main__':
    kfp.Client().create_run_from_pipeline_func(pipeline_func=mnist_pipeline, 
                                               arguments=arguments)
