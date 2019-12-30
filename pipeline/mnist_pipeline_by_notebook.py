import kfp
import kfp.dsl as dsl
import kfp.gcp as gcp
import kfp.onprem as onprem

@dsl.pipeline(
    name='MNIST',
    description='A pipeline to train and serve the MNIST example.'
)
def mnist_pipeline(model_export_dir='/mnt/export',
                   train_steps='200',
                   learning_rate='0.01',
                   batch_size='100',
                   pvc_name='task-pv-claim'):
    """
    Pipeline with three stages:
      1. train an MNIST classifier
      2. deploy a tf-serving instance to the cluster
      3. deploy a web-ui to interact with it
    """
    train = dsl.ContainerOp(
        name='train',
        image='gcr.io/kubeflow-examples/mnist/model:v20190304-v0.2-176-g15d997b',
        arguments=[
            "/opt/model.py",
            "--tf-export-dir", model_export_dir,
            "--tf-train-steps", train_steps,
            "--tf-batch-size", batch_size,
            "--tf-learning-rate", learning_rate
        ]
    )

    serve_args = [
        '--model-export-path', model_export_dir,
        '--server-name', "mnist-service"
    ]
    serve_args.extend([
        '--cluster-name', "mnist-pipeline",
        '--pvc-name', pvc_name
    ])

    serve = dsl.ContainerOp(
        name='serve',
        image='gcr.io/ml-pipeline/ml-pipeline-kubeflow-deployer:'
              'e9b96de317989a9673ef88d88fb9dab9dac3005f',
        arguments=serve_args
    )
    serve.after(train)

    web_ui = dsl.ContainerOp(
        name='web-ui',
        image='brightfly/kubeflow-deploy-service:handson',
        arguments=[
            '--image',
            'gcr.io/kubeflow-examples/mnist/web-ui:v20190304-v0.2-176-g15d997b-pipelines',
            '--name', 'web-ui',
            '--container-port', '5000',
            '--service-port', '80',
            '--service-type', "LoadBalancer",
            '--cluster-name', "mnist-pipeline"
        ]
    )
    web_ui.after(serve)

    steps = [train, serve, web_ui]
    for step in steps:
        step.apply(onprem.mount_pvc(pvc_name, 'local-storage', '/mnt'))


arguments = {'model_export_dir': '/mnt/export',
             'train_steps':'200',
             'learning_rate':'0.01',
             'batch_size':'100',
             'pvc_name':'task-pv-claim'}
if __name__ == '__main__':
    kfp.Client().create_run_from_pipeline_func(pipeline_func=mnist_pipeline,
                                               arguments=arguments)
