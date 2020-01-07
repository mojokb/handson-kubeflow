#!/usr/bin/env python2.7
'''
Copyright 2018 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''


from __future__ import print_function

import logging

import numpy as np
import tensorflow as tf
import requests
import random
import json

from PIL import Image


def get_prediction(x,
                   model_name = 'kfserving-mnist-01',
                   server_ip='10.108.37.106',
                   server_name='kfserving-mnist-01.kubeflow.example.com'):
  """
  Retrieve a prediction from a TensorFlow model server

  $ MODEL_NAME=kfserving-mnist-01
  $ INPUT_PATH=@./input-7.json
  $ CLUSTER_IP=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.clusterIP}')
  $ SERVICE_HOSTNAME=$(kubectl get inferenceservice ${MODEL_NAME} -o jsonpath='{.status.url}' -n kubeflow| cut -d "/" -f 3)

  $ curl -v -H "Host: ${SERVICE_HOSTNAME}" http://$CLUSTER_IP/v1/models/$MODEL_NAME:predict -d $INPUT_PATH

  :param image:       a MNIST image represented as a 1x784 array
  :param server_host: the address of the TensorFlow server
  :param server_port: the port used by the server
  :param server_name: the name of the server
  :param timeout:     the amount of time to wait for a prediction to complete
  :return 0:          the integer predicted in the MNIST image
  :return 1:          the confidence scores for all classes
  :return 2:          the version number of the model handling the request
  """

  # kfserving-mnist-01.kubeflow.example.com
  headers = {'Host': server_name}
  request_url = "http://" + server_ip + "/v1/models/" + model_name + ":predict"
  logging.info(" request_url " + request_url)
  logging.info(x)


  x = x.astype(np.uint8).reshape(-1, 784)
  json_x = {"instances": [{"flatten_input": []}]}
  json_x["instances"][0]["flatten_input"] = json.dumps(x.tolist())

  response = requests.post(request_url,
                           json=json_x,
                           headers=headers)
  logging.info("response:")
  logging.info(response)
  return 1


def random_mnist(save_path=None):
  """
  Pull a random image out of the MNIST test dataset
  Optionally save the selected image as a file to disk

  :param savePath: the path to save the file to. If None, file is not saved
  :return 0: a 1x784 representation of the MNIST image
  :return 1: the ground truth label associated with the image
  :return 2: a bool representing whether the image file was saved to disk
  """

  mnist = tf.keras.datasets.mnist
  (batch_x, y_train), (x_test, y_test) = mnist.load_data()
  random_num = random.randint(1, 10)
  random_x = x_test[random_num]
  random_y = y_test[random_num]
  saved = False

  if save_path is not None:
    # save image file to disk
    try:
      data = random_x.astype(np.uint8).reshape(28, 28)
      img = Image.fromarray(data, 'L')
      img.save(save_path)
      saved = True
    except Exception as e: # pylint: disable=broad-except
      logging.error("There was a problem saving the image; %s", e)
  return random_x, np.argmax(random_y), saved
