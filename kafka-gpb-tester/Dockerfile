FROM ubuntu:20.04

ARG http_proxy
ARG https_proxy

ENV http_proxy $http_proxy
ENV https_proxy $https_proxy

RUN apt-get update && \
    apt-get install -y python3 && \
    apt-get install -y python3-pip && \
    pip install -U protobuf==3.8.0 && \
    pip install confluent-kafka   


CMD /bin/bash

