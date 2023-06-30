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

import sys
from tr451_vomci_nbi_message_pb2 import Msg
from tr451_vomci_nbi_message_pb2 import Error
from confluent_kafka import Producer
from configurations import util
import global_params as GLB


COMMUNICATION_AVAILABLE_VALUE = "true"

producer = Producer(GLB.conf)

def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))


if len(sys.argv) > 1:
    if sys.argv[1] == "false":
        COMMUNICATION_AVAILABLE_VALUE = "false"


print("Setting ONU communication=", COMMUNICATION_AVAILABLE_VALUE)

vomci_msg = Msg()
vomci_error = Error()
proxy_error = Error()

#the field names are the same as the .proto file
vomci_msg.header.msg_id="1"
vomci_msg.header.sender_name="vOLTMF"
vomci_msg.header.recipient_name=GLB.VOMCI_NAME
vomci_msg.header.object_type=vomci_msg.header.VOMCI_FUNCTION
vomci_msg.header.object_name=GLB.VOMCI_NAME

vomci_onu_allignment_notification = util.read_configuration('configurations/vomci-onu-aligment-notification.json')

vomci_msg.body.request.action.input_data = bytes(vomci_onu_allignment_notification,"utf-8")

producer.produce(GLB.VOMCI_TOPIC_NAME, key="key", value=bytes(vomci_msg.SerializeToString()), callback=acked)
producer.flush()

vomci_msg = Msg()
#the field names are the same as the .proto file
vomci_msg.header.msg_id="1"
vomci_msg.header.sender_name="vOLTMF"
vomci_msg.header.recipient_name=GLB.VPROXY_NAME
vomci_msg.header.object_type=vomci_msg.header.VOMCI_PROXY
vomci_msg.header.object_name=GLB.VPROXY_NAME

vomci_onu_allignment_notification = util.read_configuration('configurations/vomci-onu-aligment-notification.json')

vomci_msg.body.request.action.input_data = bytes(vomci_onu_allignment_notification,"utf-8")

producer.produce(GLB.VPROXY_TOPIC_NAME, key="key", value=bytes(vomci_msg.SerializeToString()), callback=acked)
producer.flush()

# Wait up to 1 second for events. Callbacks will be invoked during
# this method call if the message is acknowledged.
producer.poll(1)