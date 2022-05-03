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
# Created by Andre Brizido on 15/06/2021

from tr451_vomci_nbi_message_pb2 import Msg
from tr451_vomci_nbi_message_pb2 import Error
from confluent_kafka import Producer
import socket

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

#the field names are the same as the .proto file
vomci_msg.header.msg_id="1"
vomci_msg.header.sender_name="vomci-vendor-1"
vomci_msg.header.recipient_name="vOLTMF"
vomci_msg.header.object_type=vomci_msg.header.VOMCI_FUNCTION
vomci_msg.header.object_name="vomci1"

vomci_msg.body.response.update_config_resp.status_resp.status_code=0

proxy_msg.header.msg_id="2"
proxy_msg.header.sender_name="proxy-1"
proxy_msg.header.recipient_name="vOLTMF"
proxy_msg.header.object_type=proxy_msg.header.VOMCI_PROXY
proxy_msg.header.object_name="vomci-proxy"

proxy_msg.body.response.update_config_resp.status_resp.status_code=0

producer.produce(VOMCI_TOPIC_NAME, key="key", value=bytes(vomci_msg.SerializeToString()), callback=acked)
producer.flush()
producer.produce(VPROXY_TOPIC_NAME, key="key", value=bytes(proxy_msg.SerializeToString()), callback=acked)

# Wait up to 1 second for events. Callbacks will be invoked during
# this method call if the message is acknowledged.
producer.poll(1)
