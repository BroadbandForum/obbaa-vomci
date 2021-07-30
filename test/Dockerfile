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
        kafkacat \
 && apt-get clean

ARG TAG=latest
ARG DOCKER-ORG=broadbandforum
ARG DOCKER-NAME=obbaa-vomci
ARG DOCKER-TAG=latest
ARG DOCKER-IMAGE=$(DOCKER-ORG)/$(DOCKER-NAME):$(DOCKER-TAG)
ARG DOCKER-CMD=bash

RUN mkdir -p /obbaa-vomci
# copy source code
COPY requirements.txt /obbaa-vomci/requirements.txt
RUN PYTHONPATH=/obbaa-vomci \
 && pip3 install -r /obbaa-vomci/requirements.txt
COPY . /obbaa-vomci
ENV PYTHONPATH=/obbaa-vomci
WORKDIR /obbaa-vomci

EXPOSE 8801
EXPOSE 58433
CMD ['python3 -V']
CMD python3 /obbaa-vomci/test/start_vomci.py