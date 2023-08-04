# Use a minimal image (more minimal than ubuntu:22.04)
FROM python:3.11.4

LABEL MAINTAINER="Dmitry Duplyakin <dmitry.duplyakin@nrel.gov>"

# Install base utilities
RUN apt-get update && \
    apt-get install -y build-essential  && \
    apt-get install -y wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install miniconda
#RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
#     /bin/bash ~/miniconda.sh -b -p /opt/conda

#ENV CONDA_DIR /opt/conda

# Put conda in path so we can use conda activate
#ENV PATH=$CONDA_DIR/bin:$PATH

#RUN conda update -n base -c defaults conda -y

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

# Configuration for hsds endpoint 
#COPY .hscfg /root/.hscfg 

# RUN conda env create -f environment.yml
#RUN conda env create -f environment-fixedversions.yml

# Updated on 07/19/2023 to use latest Django versions
#RUN conda install -c conda-forge -n base Django -y
#RUN conda install -c conda-forge -n dw-tap-api Django -y

# Install dw_tap package
RUN git clone https://github.com/NREL/dw-tap.git
RUN cd dw-tap && python setup.py install && cd ..

EXPOSE 80

# Conda env in the path below needs to match the name in the first line of environment.yml
#CMD ["/opt/conda/envs/dw-tap-api/bin/python", "api.py", "--production"]
CMD ["python", "api.py", "--production"]

