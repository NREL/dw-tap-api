# FROM ubuntu:20.04
FROM ubuntu:22.04

LABEL MAINTAINER="Dmitry Duplyakin <dmitry.duplyakin@nrel.gov>"

# Install base utilities
RUN apt-get update && \
    apt-get install -y build-essential  && \
    apt-get install -y wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install miniconda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
     /bin/bash ~/miniconda.sh -b -p /opt/conda

ENV CONDA_DIR /opt/conda

# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/bin:$PATH


WORKDIR /app
COPY . /app

RUN conda env create -f environment.yml

EXPOSE 80

# Conda env in the path below needs to match the name in the first line of environment.yml
CMD ["/opt/conda/envs/dw-tap-api/bin/python", "api.py", "--production"]
