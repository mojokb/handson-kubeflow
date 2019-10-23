# Mnist를 모델 개발부터 서빙까지 with kubeflow.

## GOAL
쿠버네티스의 ML Toolkit인 kubeflow로 ML workflow인 모델개발 -> 튜닝 -> 서빙 까지 해보는 것이 이번 핸즈온의 Goal입니다.  


## Prerequisites
local 진행이기 때문에 kubeflow설치를 위해 minikube를 사용합니다.  
기본OS는 macOS로 진행합니다. 그 외 OS는 관련 설치 문서 참조 부탁드립니다.  
(arrikto miniKF 사용시 kubeflow가 설치되어 있기때문에 별도의 kubeflow 설치가 필요 없습니다.)  

### Install minikube
- https://minikube.sigs.k8s.io/docs/start/macos/ 참조
    ```
    $ minikube start --kubernetes-version v1.14.1 --cpus 4 --memory 8096 --disk-size=40g
    ```    

### Install kubeflow in minikube

- Deploying Kubeflow on Existing Clusters  
- Kubeflow Deployment with kfctl_k8s_istio
    ```
    $ wget https://github.com/kubeflow/kubeflow/releases/download/v0.6.2/kfctl_v0.6.2_darwin.tar.gz
    $ tar -xvf kfctl_v0.6.2_darwin.tar.gz
    
    # Add kfctl to PATH, to make the kfctl binary easier to use.
    # Use only alphanumeric characters or - in the directory name.
    $ export PATH=$PATH:"<path-to-kfctl>"
    $ export KFAPP="<your-choice-of-application-directory-name>"
    
    # Installs Istio by default. Comment out Istio components in the config file to skip Istio installation. See https://github.com/kubeflow/kubeflow/pull/3663
    $ export CONFIG="https://raw.githubusercontent.com/kubeflow/kubeflow/v0.6-branch/bootstrap/config/kfctl_k8s_istio.0.6.2.yaml"
    
    $ kubectl create ns kubeflow-anonymous
    $ kfctl init ${KFAPP} --config=${CONFIG} -V
    $ cd ${KFAPP}
    $ kfctl generate all -V
    $ kfctl apply all -V    
    
    $ k get po -n kubeflow
    
    
    
    
    # https://github.com/istio/istio/issues/10795 port issue
    ```

### If Arrikto miniKF version
- vagrant 필요
- miniKF from  arrikto (https://www.arrikto.com/minikf/)  
    ```   
    $ vagrant init arrikto/minikf  
    $ vagrant up
    ```
## Contents

### 1. Get the mnist nueral model 
   /fairing/mnist.py 참조

### 2. Juypter - local run


### 3. Fairing - gcloud 설정 (https://cloud.google.com/sdk/docs/quickstart-linux)
   private registry가 https를 지원해준다면, 그걸로 진행하지만 그렇지 않다면 gcp를 사용해서 registry 생성

   #### GCP version
   ```
   $ curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-245.0.0-linux-x86_64.tar.gz
   $ tar zxvf google-cloud-sdk-245.0.0-linux-x86_64.tar.gz google-cloud-sdk
   $ ./google-cloud-sdk/install.sh
   $ gcloud auth login
   $ gcloud config set project handon-kubeflow

   # container-registry 관련 auth가 필요합니다.
   # https://console.cloud.google.com/apis/api/containerregistry.googleapis.com/landing?project=handon-kubeflow

   $ gcloud auth configure-docker

   # GOOGLE_APPLICATION_CREDENTIALS service account auth.json 생성 필요
   # https://console.cloud.google.com/apis/credentials?project=handon-kubeflow
   

   # gke 생성 - https://cloud.google.com/kubernetes-engine/docs/how-to/creating-a-cluster?hl=ko
   
   # 네임스페이스의 imagePullSecrets 설정 필요
   
   $ kubectl create secret docker-registry gcr-json-key \
   --docker-server=gcr.io \
   --docker-username=_json_key \
   --docker-password="$(cat ~/auth.json)" \
   --docker-email=any@valid.email
   
   # for private registry
   kubectl create secret generic regcred \
    --from-file=.dockerconfigjson=/home/vagrant/.docker/config.json \
    --type=kubernetes.io/dockerconfigjson -n kubeflow-user

   # 서비스 어카운트에 imagePullSecrets 설정
   $ kubectl patch serviceaccount default \
   -p '{"imagePullSecrets": [{"name": "gcr-json-key"}, {"name": "regcred"}]}'   
   
   # 설정 확인
   $ kubectl get serviceaccount default -o yaml 
   ```

### 4. Fairing - install fairing library in notekbook
   - pip install  
       ```
       pip3 install kubeflow-fairing
       ```
   - install from repo.  
       ```
       git clone https://github.com/kubeflow/fairing
       cd fairing
       pip3 install -r examples/prediction/requirements.txt 
       pip3 setup.py install
       ```
### 5. Fairing - simple example with my cluster.

### 6. Fairing - wrap fairing library, build model/ remote Image, submit job to cluster
   /fairing/fairing_mnist.py 참조


### 7. Katib - Tunning hyperopt. mnist
  아직 namespace scope을 지원하지 않기 때문에 katib experiment job은 kubeflow namespace로 던져야 metric collector가 생성된다  
  그래서 ServiceAccount에 kubeflow namespace의 pods, experiment resource를 사용할 수 있게 role binding 시켜줘야함.  
/fairing/kubeflow_role_binding.yaml 참조

~~~
$ kubectl apply -f mnist_experiment_random.yaml
~~~

### 8. pipeline - build model by recurring task: katib max 값을 기준으로 모델 생성/ 서빙  
https://github.com/kubeflow/examples/tree/master/pipelines/mnist-pipelines 기준 변경
```
# pipeline sdk install
$ !pip install https://storage.googleapis.com/ml-pipeline/release/latest/kfp.tar.gz --upgrade 
# /pipeline/mnist_pipeline.py 
$ python3 mnist_pipeline.py
# mnist_pipeline.tar.gz 생성 되면 파이프라인에 등록, 

# onprem용 pvc 등록
$ kubectl apply -f pvc_for_pipeline.yaml

# model-export-dir을 minio 경로로 변경하기 위해,
# 파이프 라인용 minio ui에 접속하여(NodePort or ingress) minio/ minio123, katib-model bucket 생성

```



## Install kubeflow - not arrikto

   ```
   
  # Add kfctl to PATH, to make the kfctl binary easier to use.
  # Use only alphanumeric characters or - in the directory name.
  PATH=$PATH:/Users/leemyounghwan/kubeflow_for_kind
  KFAPP=/Users/leemyounghwan/kubeflow_for_kind/handson
  # Installs Istio by default. Comment out Istio components in the config file to skip Istio installation. See https://github.com/kubeflow/kubeflow/pull/3663
  CONFIG="https://raw.githubusercontent.com/kubeflow/kubeflow/v0.6-branch/bootstrap/config/kfctl_k8s_istio.0.6.2.yaml"

  kfctl init ${KFAPP} --config=${CONFIG} -V
  cd ${KFAPP}
  kfctl generate all -V
  kfctl apply all -V
   ```

  

## Remove kubeflow
   ```
  cd ${KFAPP}
  kfctl delete all -V
   ```
