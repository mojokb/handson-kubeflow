import kfp
import kfp.dsl as dsl

@dsl.pipeline(
    name='MnistWebUi',
    description='Print HelloWorld'
)
def mnist_web_ui_pipeline():
    hello = dsl.ContainerOp(
        name='mnist_web_ui',
        image='brightfly/kfserving-mnist-web-ui-deploy:latest',
    )

if __name__ == '__main__':
    kfp.Client().create_run_from_pipeline_func(pipeline_func=mnist_web_ui_pipeline,
                                               arguments={})