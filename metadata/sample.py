# pip install kubeflow-metadata
# Install other packages:
# pip install pandas

from kubeflow.metadata import metadata
import pandas
from datetime import datetime


# create a workspace
ws1 = metadata.Workspace(
    # Connect to metadata-service in namesapce kubeflow in k8s cluster.
    backend_url_prefix="metadata-service.kubeflow:8080",
    name="ws1",
    description="a workspace for testing",
    labels={"n1": "v1"})

# create a run in a workspace
r = metadata.Run(
    workspace=ws1,
    name="run-" + datetime.utcnow().isoformat("T") ,
    description="a run in ws_1",
)

# create an execution in a run
exec = metadata.Execution(
    name = "execution" + datetime.utcnow().isoformat("T") ,
    workspace=ws1,
    run=r,
    description="execution example",
)
print("An execution is create with id %s" % exec.id)


#### execution의 log_input을 통해서 metadata 입력을 한다.

data_set = exec.log_input(
        metadata.DataSet(
            description="an example data",
            name="mytable-dump",
            owner="owner@my-company.org",
            uri="file://path/to/dataset",
            version="v1.0.0",
            query="SELECT * FROM mytable"))
assert data_set.id
print("data set id is %s" % data_set.id)

model = exec.log_output(
    metadata.Model(
            name="MNIST",
            description="model to recognize handwritten digits",
            owner="someone@kubeflow.org",
            uri="gcs://my-bucket/mnist",
            model_type="neural network",
            training_framework={
                "name": "tensorflow",
                "version": "v1.0"
            },
            hyperparameters={
                "learning_rate": 0.5,
                "layers": [10, 3, 1],
                "early_stop": True
            },
            version="v0.0.1",
            labels={"mylabel": "l1"}))
assert model.id
print("model id is %s" % model.id)