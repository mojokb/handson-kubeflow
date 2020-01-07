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

import logging
import os
from threading import Timer
import uuid

from flask import Flask, render_template, request
from mnist_client import get_prediction, random_mnist

app = Flask(__name__)




# handle requests to the server
@app.route("/")
def main():
  # get url parameters for HTML template
  model_arg = request.args.get('model', 'kfserving-mnist-01')
  server_name_arg = request.args.get('name', 'kfserving-mnist-01.kubeflow.example.com')
  server_ip_arg = request.args.get('addr', '10.108.37.106')
  args = {"model": model_arg, "server_name": server_name_arg, "server_ip": server_ip_arg}
  logging.info("Request args: %s", args)

  output = None
  connection = {"text": "", "success": False}
  img_id = str(uuid.uuid4())
  img_path = "static/tmp/" + img_id + ".png"
  logging.info("img_path " + img_path)
  try:
    # get a random test MNIST image
    x, y, _ = random_mnist(img_path)
    # get prediction from TensorFlow server
    pred = get_prediction(x,
                           model_name=model_arg,
                           server_ip=server_ip_arg,
                           server_name=server_name_arg)
    logging.info("pred " + pred)
    # if no exceptions thrown, server connection was a success
    connection["text"] = "Connected (model version: )"
    connection["success"] = True
    # parse class confidence scores from server prediction
    scores_dict = []
    for i in range(0, 10):
      scores_dict += [{"index": str(i)}]
    output = {"truth": y, "prediction": pred,
              "img_path": img_path, "scores": scores_dict}
  except Exception as e: # pylint: disable=broad-except
    logging.info("Exception occured: %s", e)
    # server connection failed
    connection["text"] = "Exception making request: {0}".format(e)
  # after 10 seconds, delete cached image file from server
  t = Timer(10.0, remove_resource, [img_path])
  t.start()
  # render results using HTML template
  return render_template('index.html', output=output,
                         connection=connection, args=args)


def remove_resource(path):
  """
  attempt to delete file from path. Used to clean up MNIST testing images

  :param path: the path of the file to delete
  """
  try:
    os.remove(path)
    print("removed " + path)
  except OSError:
    print("no file at " + path)


if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO,
                      format=('%(levelname)s|%(asctime)s'
                              '|%(pathname)s|%(lineno)d| %(message)s'),
                      datefmt='%Y-%m-%dT%H:%M:%S',
                      )
  logging.getLogger().setLevel(logging.INFO)
  logging.info("Starting flask.")
  app.run(debug=True, host='0.0.0.0')
