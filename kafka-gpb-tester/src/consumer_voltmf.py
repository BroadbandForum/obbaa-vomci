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
import nbi.grpc.service_definition.tr451_vomci_nbi_message_pb2 as tr451_vomci_nbi_message_pb2
import nbi.grpc.service_definition.tr451_vomci_nbi_service_pb2 as tr451_vomci_nbi_service_pb2
from confluent_kafka.cimpl import Consumer, KafkaException, KafkaError
import sys



conf = {'bootstrap.servers': "kafka:9092",
        'group.id': "vOLTMF",
        'auto.offset.reset': 'smallest'}


consumer = Consumer(conf)


running = True

def msg_process(msg):
    gpbmsg = Msg()
    gpbmsg.ParseFromString(msg.value())
    print("--------------------------------------")
    print("Message received:")
    print("--------------------------------------")
    #the field names are the same as the .proto file
    print("msg.header.msg_id="             + gpbmsg.header.msg_id               )
    print("msg.header.sender_name="        + gpbmsg.header.sender_name          )
    print("msg.header.recipient_name="     + gpbmsg.header.recipient_name       )
    print("msg.header.object_type="        + str(gpbmsg.header.object_type)       )
    print("msg.header.object_name="        + str(gpbmsg.header.object_name)       )

    
    if gpbmsg.body.WhichOneof("msg_body") == "request":
        if gpbmsg.body.request.WhichOneof("req_type") == "rpc":
            print("msg.body.request.rpc.input_data="+ gpbmsg.body.request.rpc.input_data.decode("utf-8") )
        elif gpbmsg.body.request.WhichOneof("req_type") == "action":
            print("msg.body.request.action.input_data=" + gpbmsg.body.request.action.input_data.decode("utf-8"))
        elif gpbmsg.body.request.WhichOneof("req_type") == "hello":  
            print("msg.body.request.hello.service_endpoint_name="+ gpbmsg.body.request.hello.service_endpoint_name) 
        else:
            print("###request type not implemented:" + gpbmsg.body.request.WhichOneof("req_type"))
    elif gpbmsg.body.WhichOneof("msg_body") == "response":
        if gpbmsg.body.response.WhichOneof("resp_type") == "rpc_resp":
            if gpbmsg.body.response.rpc_resp.status_resp.status_code == 0:
                print("msg.body.response.rpc_resp.status_resp.status_code=OK")
            elif gpbmsg.body.response.rpc_resp.status_resp.status_code == 1:
                print("msg.body.reponse.rpc_resp.status_resp.status_code=GENERAL_ERROR")
                print("msg.body.response.rpc_resp.status_resp.error.error_type="+ str(gpbmsg.body.response.rpc_resp.status_resp.error[0].error_type))
                print("msg.body.response.rpc_resp.status_resp.error.error_tag=" + str(gpbmsg.body.response.rpc_resp.status_resp.error[0].error_tag))
                print("msg.body.response.rpc_resp.status_resp.error.error_severity=" + str(gpbmsg.body.response.rpc_resp.status_resp.error[0].error_severity))
                print("msg.body.response.rpc_resp.status_resp.error.error_app_tag=" + str(gpbmsg.body.response.rpc_resp.status_resp.error[0].error_app_tag))
                print("msg.body.response.rpc_resp.status_resp.error.error_path=" + str(gpbmsg.body.response.rpc_resp.status_resp.error[0].error_path))
                print("msg.body.response.rpc_resp.status_resp.error.error_message=" + str(gpbmsg.body.response.rpc_resp.status_resp.error[0].error_message))
            else:
                print("### invalid status code")

        elif gpbmsg.body.response.WhichOneof("resp_type") == "action_resp":
            if gpbmsg.body.response.action_resp.status_resp.status_code == 0:
                print("msg.body.response.action_resp.status_resp.status_code=OK")
            elif gpbmsg.body.response.action_resp.status_resp.status_code == 1:
                print("msg.body.reponse.action_resp.status_resp.status_code=GENERAL_ERROR")
                print("msg.body.response.action_resp.status_resp.error.error_type=" + str(gpbmsg.body.response.action_resp.status_resp.error[0].error_type))
                print("msg.body.response.action_resp.status_resp.error.error_tag=" + str(gpbmsg.body.response.action_resp.status_resp.error[0].error_tag))
                print("msg.body.response.action_resp.status_resp.error.error_severity=" + str(gpbmsg.body.response.action_resp.status_resp.error[0].error_severity))
                print("msg.body.response.action_resp.status_resp.error.error_app_tag=" + str(gpbmsg.body.response.action_resp.status_resp.error[0].error_app_tag))
                print("msg.body.response.action_resp.status_resp.error.error_path=" + str(gpbmsg.body.response.action_resp.status_resp.error[0].error_path))
                print("msg.body.response.action_resp.status_resp.error.error_message=" + str(gpbmsg.body.response.action_resp.status_resp.error[0].error_message))
            
            else:
                print("### invalid status code")

        elif gpbmsg.body.response.WhichOneof("resp_type") == "hello_resp":
            if gpbmsg.body.response.hello_resp.service_endpoint_name == "voltmf":
                print("\n\n\n")
                print("--------------------------------------")
                print("Hello Response Message:")
                print("--------------------------------------")
                print("msg.body.response.hello_resp.service_endpoint_name=" + gpbmsg.body.response.hello_resp.service_endpoint_name)
                print("\n\n\n")

        else:
            print("###response type not implemented:" + gpbmsg.body.response.WhichOneof("resp_type"))

    elif gpbmsg.body.WhichOneof("msg_body") == "notification":
                print("\n\n\n")
                print("--------------------------------------")
                print("Hello Notification Message:")
                print("--------------------------------------")
                print("msg.body.notification.data="+ gpbmsg.body.notification.data.decode("utf-8") )
                print("\n\n\n")
    else:
        print ("###body type not implemented:" + gpbmsg.body.WhichOneof("msg_body"))

def basic_consume_loop(consumer, topics):
    print("Consuming from topics:")
    print(topics)

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
    
    
basic_consume_loop(consumer, ["VOMCI_REQUEST"])
