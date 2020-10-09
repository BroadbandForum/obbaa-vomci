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


