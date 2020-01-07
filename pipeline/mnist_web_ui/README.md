# Mnist - KFServing UI on Kubeflow

KFServing로 올라간 Tensorflow serving server와 연동하는 Web-UI web application. https://github.com/kubeflow/examples/tree/master/mnist/web-ui에서 mnist_client를 KFServing에 맞게 수정   

- flask_server.py : Model name, Server name, Server IP(ClusterIP) 입력받게 변경
- mnist_client.py : kfserving 접속을 위해 request 사용, random mnist image 생성을 위해 tf.keras.datasets.mnist 사용


~~~
$ docker build --tag ${web-ui-server} .
$ sudo docker run -p 19000:5000 ${web-ui-server}

INFO|2020-01-07T18:26:52|flask_server.py|95| Starting flask.
 * Serving Flask app "flask_server" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: on
INFO|2020-01-07T18:26:52|/usr/local/lib/python2.7/dist-packages/werkzeug/_internal.py|122|  * Running on htt
p://0.0.0.0:5000/ (Press CTRL+C to quit)
INFO|2020-01-07T18:26:52|/usr/local/lib/python2.7/dist-packages/werkzeug/_internal.py|122|  * Restarting wit
h stat
INFO|2020-01-07T18:26:54|/home/flask_server.py|95| Starting flask.
WARNING|2020-01-07T18:26:54|/usr/local/lib/python2.7/dist-packages/werkzeug/_internal.py|122|  * Debugger is
 active!
INFO|2020-01-07T18:26:54|/usr/local/lib/python2.7/dist-packages/werkzeug/_internal.py|122|  * Debugger PIN: 
249-821-232
INFO|2020-01-07T18:27:06|/home/flask_server.py|38| Request args: {'model': 'kfserving-mnist-01', 'name': 'kf
serving-mnist-01.kubeflow.example.com', 'addr': '10.108.37.106'} 

~~~