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
ARG DOCKER-NAME=obbaa-vproxy
ARG DOCKER-TAG=latest
ARG DOCKER-IMAGE=$(DOCKER-ORG)/$(DOCKER-NAME):$(DOCKER-TAG)
ARG DOCKER-CMD=bash

RUN mkdir -p /obbaa-vproxy
# copy source code
COPY requirements.txt /obbaa-vproxy/requirements.txt
RUN PYTHONPATH=/obbaa-vproxy \
 && pip3 install -r /obbaa-vproxy/requirements.txt
COPY . /obbaa-vproxy
ENV PYTHONPATH=/obbaa-vproxy
WORKDIR /obbaa-vproxy
EXPOSE 8433
CMD ['python3 -V']
CMD python3 bin/start_vproxy.py
