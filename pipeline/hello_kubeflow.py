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
    kfp.Client().create_run_from_pipeline_func(pipeline_func=hellokubelfow_pipeline, arguments={})

    # 파이프라인 파일로 등록시
    # kfp.compiler.Compiler().compile(hellokubelfow_pipeline, 'containerop.pipeline.tar.gz')    
    # dsl-compile 툴을 이용할 경우
    # $ dsl-compile --py containerop.py --output containerop.pipeline.tar.gz
