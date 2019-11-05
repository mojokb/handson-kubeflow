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

        DOCKER_REGISTRY = 'registry.zipsacoding.com'
        fairing.config.set_builder(
            'append',
            image_name='katib-job',
            base_image='gcr.io/kubeflow-images-public/tensorflow-2.0.0a0-notebook-gpu:v0.7.0',
            registry=DOCKER_REGISTRY, 
            push=True)
        # cpu 1, memory 1GiB
        fairing.config.set_deployer('job',
                                    pod_spec_mutators=[
                                        k8s_utils.get_resource_mutator(cpu=2,
                                                                       memory=5)]
         
                                   )
        # python3         
        fairing.config.set_preprocessor('python', input_files=[__file__])
        fairing.config.run()
    else:
        remote_train = MyModel()
        remote_train.train()
