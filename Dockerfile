# FROM ubuntu:latest
FROM ubuntu:22.10

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

RUN conda update -n base -c defaults conda -y

WORKDIR /app
COPY . /app

#RUN conda install -y openssl==1.1.1p

RUN conda env create -f environment.yml

# Testing downgrading numpy
#RUN conda install numpy==1.22.0 -n dw-tap-api -c conda-forge -y

EXPOSE 80

# Conda env in the path below needs to match the name in the first line of environment.yml
CMD ["/opt/conda/envs/dw-tap-api/bin/python", "api.py", "--production"]
