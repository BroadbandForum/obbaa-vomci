ARG FROM=broadbandforum/sphinx:latest
FROM $FROM

# install OS packages and create directories
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get --yes install \
        make \
        net-tools \
        iputils-ping \
        python3 \
        python3-pip \
        tshark \
        vim \
 && apt-get clean

ARG TAG=latest
ARG DOCKER-ORG=broadbandforum
ARG DOCKER-NAME=test-voltmf
ARG DOCKER-TAG=latest
ARG DOCKER-IMAGE=$(DOCKER-ORG)/$(DOCKER-NAME):$(DOCKER-TAG)
ARG DOCKER-CMD=bash

RUN mkdir -p /test-voltmf
# copy source code
COPY requirements.txt /test-voltmf/requirements.txt
RUN PYTHONPATH=/test-voltmf \
 && pip3 install -r /test-voltmf/requirements.txt
COPY . /test-voltmf
ENV PYTHONPATH=/test-voltmf
WORKDIR /test-voltmf
EXPOSE 8484
CMD ['python3 -V']
CMD python3 test/test_voltmf/start_test_voltmf.py
