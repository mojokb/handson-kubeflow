import os
import tensorflow as tf

class MyModel(object):
  def train(self):
    mnist = tf.keras.datasets.mnist

    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_train, x_test = x_train / 255.0, x_test / 255.0

    model = tf.keras.models.Sequential([
      tf.keras.layers.Flatten(input_shape=(28, 28)),
      tf.keras.layers.Dense(128, activation='relu'),
      tf.keras.layers.Dropout(0.2),
      tf.keras.layers.Dense(10, activation='softmax')
    ])

    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    model.fit(x_train, y_train, epochs=5)

    model.evaluate(x_test,  y_test, verbose=2)

if __name__ == '__main__':
    if os.getenv('FAIRING_RUNTIME', None) is None:
        from kubeflow import fairing
        from kubeflow.fairing.kubernetes import utils as k8s_utils
        
        s3_endpoint = 'minio-service.kubeflow.svc.cluster.local:9000'
        minio_endpoint = "http://"+s3_endpoint
        minio_username = "minio"
        minio_key = "minio123"
        minio_region = "us-east-1"

        from kubeflow.fairing.builders.cluster.minio_context import MinioContextSource
        minio_context_source = MinioContextSource(endpoint_url=minio_endpoint, 
                                                  minio_secret=minio_username, 
                                                  minio_secret_key=minio_key, 
                                                  region_name=minio_region)     
        
        
        output_map =  {
            "Dockerfile": "Dockerfile",
            "mnist.py": "mnist.py"
        }        

        DOCKER_REGISTRY = 'kubeflow-registry.default.svc.cluster.local:30000'
        #fairing.config.set_preprocessor('notebook', notebook_file='app.ipynb', output_map=output_map)
        fairing.config.set_preprocessor('python', output_map=output_map)
        fairing.config.set_builder(
            'cluster',
            image_name='fairing-job',
            base_image='brightfly/kubeflow-jupyter-lab:tf2.0-cpu',
            context_source=minio_context_source,
            registry=DOCKER_REGISTRY, 
            push=True)
        # cpu 1, memory 1GiB
        fairing.config.set_deployer('job',
                                    namespace='handson5',
                                    pod_spec_mutators=[
                                        k8s_utils.get_resource_mutator(cpu=1,
                                                                       memory=4)]
         
                                   )
        # python3         
        # fairing.config.set_preprocessor('python', input_files=[__file__])
        fairing.config.run()
    else:
        remote_train = MyModel()
        remote_train.train()
