FROM python:3.6

WORKDIR /jup

RUN pip install jupyter -U && pip install jupyterlab

EXPOSE 8888

ENV NB_PREFIX /

CMD ["jupyter", "lab", "--notebook-dir=/home/jovyan --ip=0.0.0.0 --no-browser --allow-root --port=8888 --NotebookApp.token='' --NotebookApp.password='' --NotebookApp.allow_origin='*' --NotebookApp.base_url=${NB_PREFIX}"]
