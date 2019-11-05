FROM jupyter/minimal-notebook

WORKDIR /home/jovyan

RUN pip install jupyterlab && \
    jupyter serverextension enable --py jupyterlab --sys-prefix

EXPOSE 8888


ENV NB_USER=jovyan
ENV NB_UID=1000
ENV NB_PREFIX /

CMD ["sh", "-c", "jupyter lab --notebook-dir=/home/jovyan --ip=0.0.0.0 --no-browser --allow-root --port=8888 --LabApp.token='' --LabApp.password='' --LabApp.allow_origin='*' --LabApp.base_url=${NB_PREFIX}"]