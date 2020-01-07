FROM python:3.6

USER root

RUN apt-get update && apt-get install -yq --no-install-recommends \
  apt-transport-https \
  build-essential \
  bzip2 \
  ca-certificates \
  curl \
  g++ \
  git \
  gnupg \
  graphviz \
  locales \
  lsb-release \
  openssh-client \
  sudo \
  unzip \
  vim \
  wget \
  zip \
  && apt-get clean && \
  rm -rf /var/lib/apt/lists/*

RUN curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
RUN echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
RUN apt-get update
RUN apt-get install -y kubectl

RUN wget https://github.com/kubernetes-sigs/kustomize/releases/download/kustomize%2Fv3.5.3/kustomize_v3.5.3_linux_amd64.tar.gz
RUN tar xzvf kustomize_v3.5.3_linux_amd64.tar.gz
RUN mv kustomize /usr/local/bin

ADD ./deployment.yaml /mnist_web_ui/deployment.yaml
ADD ./service.yaml /mnist_web_ui/service.yaml
ADD ./kustomization.yaml /mnist_web_ui/kustomization.yaml
ADD ./src/deploy.sh /bin/.

ENTRYPOINT ["/bin/deploy.sh"]
