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
# vOMCI test consumer based on the examples in 
# https://docs.confluent.io/clients-confluent-kafka-python/current/overview.html
#
# Created by Andre Brizido on 28/01/2022

from tr451_vomci_nbi_message_pb2 import Msg
from tr451_vomci_nbi_message_pb2 import Error
from tr451_vomci_nbi_message_pb2 import NFInformation
from confluent_kafka import Producer
import socket
import global_params as GLB

conf = {'bootstrap.servers': "kafka:9092",
        'client.id': socket.gethostname()}

VOMCI_TOPIC_NAME="vomci1-response"
VPROXY_TOPIC_NAME="vomci-proxy-response"

producer = Producer(conf)

def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))

vomci_msg = Msg()
vomci_error = Error()
proxy_msg = Msg()
proxy_error = Error()

#############################
# VOMCI
#############################
#the field names are the same as the .proto file
vomci_msg.header.msg_id="1"
vomci_msg.header.sender_name="vomci1"
vomci_msg.header.recipient_name="vOLTMF"
vomci_msg.header.object_type=vomci_msg.header.VOMCI_FUNCTION
vomci_msg.header.object_name="vomci1"

vomci_msg.body.response.hello_resp.service_endpoint_name = "vomci1-endpoint"

nfInformation =  NFInformation()
capabilities= NFInformation.NFCapability.ONU_STATE_ONLY_SUPPORT
nfInformation.capabilities.extend([capabilities])
nfInformation.nf_types.update({'vendor-name' : 'Broadband Forum', 'software-version': '5.0.0'})    

vomci_msg.body.response.hello_resp.network_function_info.extend([nfInformation])


#############################
# Proxy
#############################
proxy_msg.header.msg_id="2"
proxy_msg.header.sender_name="vomci-proxy"
proxy_msg.header.recipient_name="vOLTMF"
proxy_msg.header.object_type=proxy_msg.header.VOMCI_PROXY
proxy_msg.header.object_name="vomci-proxy"

proxy_msg.body.response.hello_resp.service_endpoint_name = "vproxy-endpoint"

nfInformation =  NFInformation()
capabilities= NFInformation.NFCapability.ONU_STATE_ONLY_SUPPORT
nfInformation.capabilities.extend([capabilities])
nfInformation.nf_types.update({'vendor-name' : 'Broadband Forum', 'software-version': '5.0.0'})    

proxy_msg.body.response.hello_resp.network_function_info.extend([nfInformation])

#############################
#send all messages
#############################
producer.produce(VOMCI_TOPIC_NAME, key="key", value=bytes(vomci_msg.SerializeToString()), callback=acked)
producer.flush()
producer.produce(VPROXY_TOPIC_NAME, key="key", value=bytes(proxy_msg.SerializeToString()), callback=acked)

# Wait up to 1 second for events. Callbacks will be invoked during
# this method call if the message is acknowledged.
producer.poll(1)
