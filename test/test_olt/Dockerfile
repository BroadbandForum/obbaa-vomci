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
ARG DOCKER-NAME=test-olt
ARG DOCKER-TAG=latest
ARG DOCKER-IMAGE=$(DOCKER-ORG)/$(DOCKER-NAME):$(DOCKER-TAG)
ARG DOCKER-CMD=bash

RUN mkdir -p /test-olt
# copy source code
COPY requirements.txt /test-olt/requirements.txt
RUN PYTHONPATH=/test-olt \
 && pip3 install -r /test-olt/requirements.txt
COPY . /test-olt
ENV PYTHONPATH=/test-olt
WORKDIR /test-olt
EXPOSE 8484
CMD ['python3 -V']
CMD python3 test/test_olt/start_test_olt.py
