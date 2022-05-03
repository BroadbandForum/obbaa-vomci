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
vomci_msg.header.sender_name="vOLTMF"
vomci_msg.header.recipient_name=GLB.VOMCI_NAME
vomci_msg.header.object_type=vomci_msg.header.ONU
vomci_msg.header.object_name=GLB.ONU_NAME

vomci_msg.body.request.replace_config.config_inst = bytes(
    "{\"bbf-qos-filters:filters\":{},\"ietf-ipfix-psamp:ipfix\":{},\"ietf-hardware:hardware\":{},\"bbf-qos-classifiers:classifiers\":{},\"ietf-pseudowires:pseudowires\":{},\"bbf-ghn:ghn\":{},\"bbf-qos-policies:qos-policy-profiles\":{},\"bbf-vdsl:vdsl\":{},\"bbf-xpongemtcont:xpongemtcont\":{},\"ietf-system:system\":{},\"bbf-qos-policer-envelope-profiles:envelope-profiles\":{},\"bbf-ghs:ghs\":{},\"ietf-interfaces:interfaces\":{},\"bbf-qos-policies:policies\":{},\"bbf-qos-traffic-mngt:tm-profiles\":{},\"bbf-qos-policing:policing-profiles\":{},\"bbf-selt:selt\":{},\"bbf-l2-dhcpv4-relay:l2-dhcpv4-relay-profiles\":{},\"ieee802-dot1x:nid-group\":{},\"ietf-alarms:alarms\":{},\"ietf-netconf-acm:nacm\":{},\"bbf-hardware-rpf-dpu:rpf\":{},\"bbf-pppoe-intermediate-agent:pppoe-profiles\":{},\"bbf-fast:fast\":{},\"bbf-mgmd:multicast\":{},\"bbf-melt:melt\":{},\"bbf-subscriber-profiles:subscriber-profiles\":{},\"bbf-ldra:dhcpv6-ldra-profiles\":{},\"bbf-l2-forwarding:forwarding\":{}}"
    ,"utf-8")

producer.produce(GLB.VOMCI_TOPIC_NAME, key="key", value=bytes(vomci_msg.SerializeToString()), callback=acked)
producer.flush()

