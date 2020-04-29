import kfp
import kfp.dsl as dsl
import kfp.onprem as onprem
from kubernetes.client.models import V1EnvVar

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
def mnist_pipeline(learning_rate, dropout_rate, checkpoint_dir, model_version, saved_model_dir, tensorboard_log):
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
            image='kubeflow-registry.default.svc.cluster.local:30000/katib-job:B67AEB5C',
            command=['python', '/app/mnist.py'],
            arguments=[
                "--learning_rate", learning_rate,
                "--dropout_rate", dropout_rate,
                "--checkpoint_dir", checkpoint_dir,
                "--model_version", model_version,
                "--saved_model_dir", saved_model_dir,
                "--tensorboard_log", tensorboard_log
            ],
            pvolumes={"/result": vop.volume},
            output_artifact_paths={'mlpipeline-ui-metadata': '/mlpipeline-ui-metadata.json'},
            container_kwargs={'env': [
                                        V1EnvVar('S3_ENDPOINT', 'minio-service.kubeflow.svc.cluster.local:9000'),
                                        V1EnvVar('AWS_ENDPOINT_URL', 'http://minio-service.kubeflow.svc.cluster.local:9000'),                                     
                                        V1EnvVar('AWS_ACCESS_KEY_ID', 'minio'),                                     
                                        V1EnvVar('AWS_SECRET_ACCESS_KEY', 'minio123'),                                  
                                        V1EnvVar('AWS_REGION', 'us-east-1'),                                                     
                                        V1EnvVar('S3_USE_HTTPS', '0'),                                                                     
                                        V1EnvVar('S3_VERIFY_SSL', '0'),                                                                                     
                                     ]}

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
             'model_version' : '001',
             'saved_model_dir':'/result/saved_model',
             'tensorboard_log': '/result/log'
            }
if __name__ == '__main__':
    kfp.Client().create_run_from_pipeline_func(pipeline_func=mnist_pipeline, 
                                               arguments=arguments)