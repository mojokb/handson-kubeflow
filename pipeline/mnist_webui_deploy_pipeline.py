import kfp
import kfp.dsl as dsl

@dsl.pipeline(
    name='MnistWebUi',
    description='web-ui by kustomize build'
)
def mnist_web_ui_pipeline():
    mnist_web_ui = dsl.ContainerOp(
        name='mnist_web_ui',
        image='brightfly/kfserving-mnist-web-ui-deploy:latest',
    )

if __name__ == '__main__':
    kfp.Client().create_run_from_pipeline_func(pipeline_func=mnist_web_ui_pipeline,
                                               arguments={})