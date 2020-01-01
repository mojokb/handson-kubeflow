import kfp
import kfp.dsl as dsl
import kfp.onprem as onprem

@dsl.pipeline(
    name='AttachStorage',
    description='Create a pvc, attach it to pipeline.'
)
def attatch_pvc_pipeline():
    
    vop = dsl.VolumeOp(
        name="volume_creation",
        resource_name="mypvc",
        storage_class="nfs-client",
        modes=dsl.VOLUME_MODE_RWM,
        size="1Gi"
    )
    
    op1 = dsl.ContainerOp(
        name='HelloKubeflow',
        image='alpine',
        command=['sh', '-c'],
        arguments=['echo "hello Kubeflow" > /mnt/content.txt'],
        pvolumes={"/mnt": vop.volume}
    )
    
    op2 = dsl.ContainerOp(
        name='cat-content',
        image='alpine',
        command=['cat'],
        arguments=['/mnt/content.txt'],
        pvolumes={"/mnt": op1.pvolume}
    )

    op1.after(vop)
    op2.after(op1)
        
     
if __name__ == '__main__':
    kfp.Client().create_run_from_pipeline_func(pipeline_func=attatch_pvc_pipeline, 
                                               arguments={})
