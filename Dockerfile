ARG BASE_IMG=python:3.7
FROM $BASE_IMG

# see output in our console 
ENV PYTHONUNBUFFERED 1
ARG CONFIG 

COPY requirements.txt /requirements.txt
COPY docker/requirements/$CONFIG.txt /requirements.$CONFIG.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev apt-utils\
    && rm -rf /var/lib/apt/lists/* \
    && python --version \
    && pip install --upgrade pip \
    && pip install matplotlib \
    && pip install --no-cache-dir -r /requirements.txt \
    && pip install --no-cache-dir -r /requirements.$CONFIG.txt \
    && apt-get purge -y --auto-remove gcc python3-dev apt-utils

ARG GRB_LICENSE_FILE
ENV GRB_LICENSE_FILE $GRB_LICENSE_FILE
