# OB-BAA vOMCI Proxy and vOMCI Function
This repository contains the vOMCI Function and Proxy used in the [OB-BAA implementation](https://github.com/BroadbandForum/obbaa).

The vOMCI Function, also known as the vOMC PF (Processing Function), and vOMCI Proxy provide the capabilities needed to:
- Translate YANG request/responses and notifications to/from the vOLTMF into the OMCI messages
- Transmit and receive request/responses and notification to/from the OLT
The vOMC PF (Processing Function), and vOMCI Proxy are deployed as microservices in separate containers 

>Note: In this release there is a limitation of a single vOMCI Proxy instance for each OLT.

## Components 
### vOMCI Function
The vOMCI function, is deployed as a microservice, is responsible for:
- Receiving service configurations from the vOLT Management function
- Translating the received configurations into ITU G.988 OMCI management entities (ME) and formatting them into OMCI messages
- Encapsulating and sending (receiving and de-encapsulating) formatted OMCI messages (ultimately targeting the ONU attached to the OLT) to (from) the vOMCI Proxy
- Translating the OMCI messages (representing ONU’s operational data) received from the vOMCI Proxy into data (e.g. notifications, acknowledges, alarms, PM registers) understandable by the vOLT Management function
- Sending the above ONU operational data to the vOLT Management function
###  vOMCI Proxy
The vOMCI Proxy works as an aggregation and interception point that avoids the need for an OLT to directly connect to individual vOMCI functions and can act as a control/interception point between the OLT and vOMCI function that is useful for troubleshooting and other management purposes (e.g., security). As the aggregation/interception point, the vOMCI Proxy is responsible for maintaining the associations between OLTs and the corresponding vOMCI functions.
 >Note: In this release there is a limitation of a single vOMCI Proxy instance for each OLT.
>
##  Docker Image Instructions:
The following command must be run in the vOMCI subdirectory of the source code in order to create the docker images
`make docker-build`

##  Run via docker-compose
This is an example docker-compose snippet to test functionality. It does not include BAA.
Save as `docker-compose.yml` and start with `docker-compose up -d`.
```
version: '3.5'
networks:
    baadist_default:
        driver: bridge
        name: baadist_default

services:
    zookeeper:
      image: confluentinc/cp-zookeeper:5.5.0
      hostname: zookeeper
      container_name: zookeeper
      environment:
        ZOOKEEPER_CLIENT_PORT: 2181
        ZOOKEEPER_TICK_TIME: 2000
      networks:
        - baadist_default

    kafka:
      image: confluentinc/cp-kafka:5.5.0
      hostname: kafka
      container_name: kafka
      depends_on:
        - zookeeper
      environment:
        KAFKA_BROKER_ID: 1
        KAFKA_ZOOKEEPER_CONNECT: 'zookeeper:2181'
        KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
        KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092
        KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
        KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      networks:
        - baadist_default

    vomci:
      image: broadbandforum/obbaa-vomci
      hostname: obbaa-vomci
      container_name: obbaa-vomci
      ports:
        - 8801:8801
      environment:
        GRPC_SERVER_NAME: vOMCIProxy
        LOCAL_GRPC_SERVER_PORT: 58433
        # Kafka bootstrap server, please provide only one address
        KAFKA_BOOTSTRAP_SERVER: "kafka:9092"
        # List of Consumer topics, seperated by spaces
        KAFKA_REQUEST_TOPICS: "OBBAA_ONU_REQUEST OBBAA_ONU_NOTIFICATION"
        KAFKA_RESPONSE_TOPIC: 'OBBAA_ONU_RESPONSE'
      networks:
        - baadist_default
      depends_on:
        - zookeeper
        - kafka
```
