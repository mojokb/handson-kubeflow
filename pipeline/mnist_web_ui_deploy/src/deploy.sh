#!/bin/bash -e

# Copyright 2018 The Kubeflow Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -x

KUBERNETES_NAMESPACE="${KUBERNETES_NAMESPACE:-kubeflow}"
NAME="kf-mnist-webui-service"

kustomize build /mnist_web_ui | kubectl apply -f -

# Wait for the ip address
timeout="1000"
start_time=`date +%s`
NODE_PORTS=""
while [ -z "$NODE_PORTS" ]; do
  NODE_PORTS=$(kubectl get svc -n $KUBERNETES_NAMESPACE $NAME -o jsonpath='{.spec.ports[0].nodePort}' 2> /dev/null)
  current_time=`date +%s`
  elapsed_time=$(expr $current_time + 1 - $start_time)
  if [[ $elapsed_time -gt $timeout ]];then
    echo "timeout"
    exit 1
  fi
  sleep 5
done
echo "service active NodePort: $NODE_PORTS"
