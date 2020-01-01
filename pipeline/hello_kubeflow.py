import kfp
import kfp.dsl as dsl

@dsl.pipeline(
    name='HelloKubeflow',
    description='Print HelloWorld'
)
def hellokubelfow_pipeline():
    hello = dsl.ContainerOp(
        name='HelloKubeflow',
        image='alpine',
        command=['sh', '-c'],
        arguments=['echo "hello Kubeflow"']
    )

if __name__ == '__main__':
    kfp.Client().create_run_from_pipeline_func(pipeline_func=hellokubelfow_pipeline, 
                                               arguments={})
