#!/usr/bin/env python
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
from confluent_kafka import Consumer
from confluent_kafka.cimpl import Consumer, KafkaException, KafkaError
import sys

import global_params as GLB

conf = {'bootstrap.servers': "kafka:9092",
        'group.id': "vOLTMF",
        'auto.offset.reset': 'smallest'}

VOMCI_TOPIC_NAME=GLB.VOMCI_RESPONSE_TOPIC_NAME
VPROXY_TOPIC_NAME=GLB.VPROXY_RESPONSE_TOPIC_NAME

consumer = Consumer(conf)



running = True

def msg_process(msg):
    gpbmsg = Msg()
    gpbmsg.ParseFromString(msg.value())
    print("--------------------------------------")
    print("Message received:")
    print("--------------------------------------")
    print(gpbmsg)
    

    if gpbmsg.body.WhichOneof("msg_body") == "request":
        if gpbmsg.body.request.WhichOneof("req_type") == "rpc":
            print("### rpc input_data="+ gpbmsg.body.request.rpc.input_data.decode("utf-8") )
        elif gpbmsg.body.request.WhichOneof("req_type") == "action":
            print("### action input_data=" + gpbmsg.body.request.action.input_data.decode("utf-8"))
            
    elif gpbmsg.body.WhichOneof("msg_body") == "response":
        if gpbmsg.body.response.WhichOneof("resp_type") == "rpc_resp":
            if gpbmsg.body.response.action_resp.status_resp.status_code == 0:
                print("### Response is an OK")
            elif gpbmsg.body.response.action_resp.status_resp.status_code == 1:
                print("### Response is a GENERAL ERROR")
            else:
                print("### invalid status code")


        elif gpbmsg.body.response.WhichOneof("resp_type") == "action_resp":
            if gpbmsg.body.response.action_resp.status_resp.status_code == 0:
                print("### Response is an OK")
            elif gpbmsg.body.response.action_resp.status_resp.status_code == 1:
                print("Response is a GENERAL ERROR")
            else:
                print("### invalid status code")


def basic_consume_loop(consumer, topics):
    print("Consuming from topics:")
    print(str(topics))
    try:
        consumer.subscribe(topics)

        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                msg_process(msg)
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

def shutdown():
    running = False
    
if len(sys.argv) > 1:
    if sys.argv[1] == "--no-proxy":    
        basic_consume_loop(consumer, [VOMCI_TOPIC_NAME])
    else:
        print("Invalid arg:", sys.argv[1])
else:
    basic_consume_loop(consumer, [VOMCI_TOPIC_NAME, VPROXY_TOPIC_NAME])
