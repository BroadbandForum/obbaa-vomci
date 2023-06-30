ARG FROM=broadbandforum/sphinx:latest
FROM $FROM

ARG http_proxy
ARG https_proxy

ENV http_proxy $http_proxy
ENV https_proxy $https_proxy

#this should be the file from the root, but we canno refer
#to files outside the build path
COPY requirements.txt /kafka-gpb-tester/requirements.txt
COPY ./kafka-gpb-tester /kafka-gpb-tester/
RUN apt-get update && \
    apt-get install -y python3 && \
    apt-get install -y python3-pip && \   
    pip install confluent-kafka && \    
    pip3 install -r /kafka-gpb-tester/requirements.txt

EXPOSE 3001

CMD python3 /kafka-gpb-tester/src/rest_api.py