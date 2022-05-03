#!/usr/bin/env python
#
#Copyright 2021 Broadband Forum
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.
#
# Created by Andre Brizido (Altice Labs) on 10/09/2021

import socket


conf = {'bootstrap.servers': "kafka:9092",
        'client.id': socket.gethostname()}




VOMCI_TOPIC_NAME="vomci1-request"
VPROXY_TOPIC_NAME="vomci-proxy-request"

VOMCI_RESPONSE_TOPIC_NAME="vomci1-response"
VPROXY_RESPONSE_TOPIC_NAME="vomci-proxy-response"

VOMCI_NAME="vomci1"
VPROXY_NAME="proxy-1"

ONU_NAME="ont1"
CT_NAME="CT_1"
ONU_ID="1"
OLT_NAME="OLT1"

VOMCI_REMOTE_ENDPOINT="proxy-grpc-1"

VPROXY_VOLTMF_ENDPOINT="vOMCi-grpc-1"
VPROXY_OLT_ENDPOINT="olt-grpc-2"


