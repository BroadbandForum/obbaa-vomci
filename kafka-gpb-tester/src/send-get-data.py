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
# Created by Jafar Hamin (Nokia) on 25/03/2022

from tr451_vomci_nbi_message_pb2 import Msg
from tr451_vomci_nbi_message_pb2 import Error
from confluent_kafka import Producer
from configurations import util
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
vomci_msg.header.sender_name="vOLTMF"
vomci_msg.header.recipient_name=GLB.VOMCI_NAME
vomci_msg.header.object_type=vomci_msg.header.ONU
vomci_msg.header.object_name=GLB.ONU_NAME


get_hw_if = util.read_configuration('configurations/get_hw_if.json')
get_hw = util.read_configuration('configurations/get_hw.json')
get_if = util.read_configuration('configurations/get_if.json')
get_all_alarms = util.read_configuration('configurations/get_all_alarms.json')

vomci_msg.body.request.get_data.filter.append(bytes(get_all_alarms,"utf-8"))

producer.produce(GLB.VOMCI_TOPIC_NAME, key="key", value=bytes(vomci_msg.SerializeToString()), callback=acked)
producer.flush()
