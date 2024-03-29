#!/usr/bin/env python
#
#Copyright 2022 Broadband Forum
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

from tr451_vomci_nbi_message_pb2 import Msg
from tr451_vomci_nbi_message_pb2 import Error
from confluent_kafka import Producer
import global_params as GLB


producer = Producer(GLB.conf)

def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced: %s" % (str(msg)))


vomci_msg = Msg()
vomci_error = Error()
proxy_error = Error()

#the field names are the same as the .proto file
vomci_msg.header.msg_id="3"
vomci_msg.header.sender_name="bbf-vomci"
vomci_msg.header.recipient_name="vOLTMF"
vomci_msg.header.object_type=vomci_msg.header.ONU
vomci_msg.header.object_name="ont1"

vomci_msg.body.notification.event_timestamp = bytes("2022-03-25T03:36:49+00:00","utf-8")
vomci_msg.body.notification.data = bytes(
    "{ \"ietf-alarms:alarms\": {\"alarm-notification\": {\"resource\": \"/ietf-interfaces:interfaces/interface[name=\'enet_uni_ont1_1_1\']\",\"alarm-type-id\": \"bbf-obbaa-ethernet-alarm-types:los\",\"alarm-type-qualifier\": \"\",\"time\": \"2022-03-25T03:36:49+00:00\",\"perceived-severity\": \"major\",\"alarm-text\": \"Loss of signal detected\"}}}"
    ,"utf-8")

producer.produce("vomci1-notification", key="key", value=bytes(vomci_msg.SerializeToString()), callback=acked)
producer.flush()

