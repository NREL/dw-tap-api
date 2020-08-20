FROM continuumio/miniconda3

LABEL MAINTAINER="Dmitry Duplyakin <dmitry.duplyakin@nrel.gov>"

WORKDIR /app
COPY . /app

RUN conda env create -f environment.yml

EXPOSE 80

# Conda env in the path below needs to match the name in the first line of environment.yml
CMD ["/opt/conda/envs/dw-tap-api/bin/python", "api.py"]
