import kfp
import kfp.dsl as dsl
import kfp.onprem as onprem
from kubernetes.client.models import V1EnvVar
from kfp import components

def echo_op(text):
    return dsl.ContainerOp(
        name='echo',
        image='library/bash:4.4.23',
        command=['sh', '-c'],
        arguments=['echo "$0"', text],
    )

kfserving_op = components.load_component_from_url('https://raw.githubusercontent.com/kubeflow/pipelines/master/components/kubeflow/kfserving/component.yaml')
    
@dsl.pipeline(
    name='MnistPipeline',
    description='mnist '
)
def mnist_pipeline(volume_size, learning_rate, dropout_rate, checkpoint_dir, model_version,
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
            image='kubeflow-registry.default.svc.cluster.local:30000/katib-job:8EA9F526',
            command=['python', '/app/save_model_mnist.py'],
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
        '''
        kfserving = dsl.ContainerOp(
            name='kfserving',
            image='kubeflow-registry.default.svc.cluster.local:30000/kfserving:D0BE75E',
            command=['python', '/app/kfserving_fairing.py'],
            arguments=[
                "--namespace", namespace,
                "--storage_uri", "pvc://" + str(vop.volume.persistent_volume_claim.claim_name) + str(storage_uri),
                "--name", name
            ],
            pvolumes={"/result": mnist.pvolume}
        )
        '''
        kfserving = kfserving_op(action = 'update',
                         model_name=name,
                         default_model_uri="pvc://" + str(vop.volume.persistent_volume_claim.claim_name) + str(storage_uri),
                         canary_model_uri='',
                         canary_model_traffic_percentage='0',
                         namespace='kubeflow',
                         framework='tensorflow',
                         default_custom_model_spec='{}',
                         canary_custom_model_spec='{}',
                         autoscaling_target='0',
                         kfserving_endpoint='')

        
        mnist_web_ui = dsl.ContainerOp(
            name='mnist_web_ui',
            image='brightfly/kfserving-mnist-web-ui-deploy:latest',
        )

        mnist.after(vop)
        result.after(mnist)
        kfserving.after(mnist)
        mnist_web_ui.after(kfserving)

arguments = {'volume_size' : '5Gi',
             'learning_rate': '0.01',
             'dropout_rate': '0.2',
             'checkpoint_dir': '/result/training_checkpoints',
             'model_version' : '001',  
             'saved_model_dir': '/result/saved_model',
             'tensorboard_log': '/result/log',
             'namespace': 'kubeflow',
             'storage_uri': '/saved_model',
             'name': 'kfserving-mnist-01'
             }

if __name__ == '__main__':
    kfp.Client().create_run_from_pipeline_func(pipeline_func=mnist_pipeline,
                                               arguments=arguments)
