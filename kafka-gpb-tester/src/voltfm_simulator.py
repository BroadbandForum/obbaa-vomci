# Copyright 2022 Broadband Forum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Created by Jafar Hamin (Nokia) in August 2022

from copy import deepcopy
from tr451_vomci_nbi_message_pb2 import Msg
from confluent_kafka import Producer
from confluent_kafka import Consumer
from confluent_kafka.cimpl import Consumer, KafkaException, KafkaError
import socket
import logging

logger = logging.getLogger('voltmf-simu')

vomci1_responses = {}
vomci2_responses = {}
vomci3_responses = {}
vproxy_responses = {}
vomci1_notifications = []
vomci2_notifications = []
vomci3_notifications = []
vproxy_notifications = []
vomci1_telemetry = []
vomci2_telemetry = []
vomci3_telemetry = []

VOMCI1_REQUEST_TOPIC_NAME = "vomci1-request"
VOMCI2_REQUEST_TOPIC_NAME = "vomci2-request"
VOMCI3_REQUEST_TOPIC_NAME = "vomci3-request"
VPROXY_REQUEST_TOPIC_NAME = "vomci-proxy-request"

VOMCI1_RESPONSE_TOPIC_NAME = "vomci1-response"
VOMCI2_RESPONSE_TOPIC_NAME = "vomci2-response"
VOMCI3_RESPONSE_TOPIC_NAME = "vomci3-response"
VPROXY_RESPONSE_TOPIC_NAME = "vomci-proxy-response"

VOMCI1_NOTIFICATION_TOPIC_NAME = "vomci1-notification"
VOMCI2_NOTIFICATION_TOPIC_NAME = "vomci2-notification"
VOMCI3_NOTIFICATION_TOPIC_NAME = "vomci3-notification"
VPROXY_NOTIFICATION_TOPIC_NAME = "vomci-proxy-notification"

VOMCI1_TELEMETRY_TOPIC_NAME = "vomci1-telemetry"
VOMCI2_TELEMETRY_TOPIC_NAME = "vomci2-telemetry"
VOMCI3_TELEMETRY_TOPIC_NAME = "vomci3-telemetry"

producer = Producer({'bootstrap.servers': "kafka:9092", 'client.id': socket.gethostname()})
consumer = Consumer({'bootstrap.servers': "kafka:9092", 'group.id': "vOLTMF", 'auto.offset.reset': 'smallest'})


def send_yang_request(request):
    request_type = request['request_type']
    object_type = request['object_type']
    recipient_name = request['recipient_name']
    if recipient_name not in recipient_name_kafka_request_topic:
        logger.error('Recipient name is not supported: ', recipient_name)
        return False
    topic = recipient_name_kafka_request_topic[recipient_name]
    if object_type not in object_type_header:
        logger.error('Object type is not supported: ', object_type)
        return False
    clear_response(request['msg_id'], recipient_name)
    msg = Msg()
    header_message(msg, request)
    if request_type == MessageData.ACTION:
        msg.body.request.action.input_data = bytes(request['action'], "utf-8")
    elif request_type == MessageData.REPLACE_CONFIG:
        msg.body.request.replace_config.config_inst = bytes(request['config'], "utf-8")
    elif request_type == MessageData.UPDATE_CONFIG:
        update_config_type = request['update_config_type']
        if update_config_type == MessageData.UPDATE_CONFIG_INST:
            msg.body.request.update_config.update_config_inst.current_config_inst = bytes(request['current_config'], "utf-8")
            msg.body.request.update_config.update_config_inst.delta_config = bytes(request['delta_config'], "utf-8")
        elif update_config_type == MessageData.UPDATE_CONFIG_REPLICA:
            msg.body.request.update_config.update_config_replica.delta_config =bytes(request['delta_config'], "utf-8")
        else:
            logger.error('update config type is not supported: ', update_config_type)
            return False            
    elif request_type == MessageData.GET_DATA:
        msg.body.request.get_data.filter.append(bytes(request['filter'], "utf-8"))
    else:
        logger.error('Request type is not supported: ', request['request_type'])
        return False
    send_message(msg, topic)
    return True

def clear_response(msg_id, recipient_name):
    recipient_name_kafka_response_messages[recipient_name][msg_id] = None

def get_vnf_response(msg_id, object_name):
    messages = recipient_name_kafka_response_messages[object_name]
    if msg_id in messages:
        return messages[msg_id]
    return None

def get_and_clear_vnf_notifications(object_name):
    messages = recipient_name_kafka_notification_messages[object_name]
    result = deepcopy(messages)
    messages.clear()
    return result

def get_and_clear_vnf_telemetry(object_name):
    messages = recipient_name_kafka_telemetry_messages[object_name]
    result = deepcopy(messages)
    messages.clear()
    return result

def header_message(msg, request):
    msg.header.msg_id = request['msg_id']
    msg.header.sender_name= request['sender_name']
    msg.header.recipient_name= request['recipient_name']
    msg.header.object_type= object_type_header[request['object_type']]
    msg.header.object_name= request['object_name']

def acked(err, msg):
    if err is not None:
        logger.error("Failed to deliver message: \n", str(err))

def send_message(msg, topic):
    producer.produce(topic, key="key", value=bytes(msg.SerializeToString()), callback=acked)
    producer.flush()

def process_received_message(msg):
    topic = msg.topic()
    logger.info('A message is received form topic: %s', topic)
    gpbmsg = Msg()
    gpbmsg.ParseFromString(msg.value())    
    logger.info(gpbmsg)
    if topic in kafka_response_topic_messages:
        messages = kafka_response_topic_messages[topic]
        messages[str(gpbmsg.header.msg_id)] = str(gpbmsg.body)
    elif topic in kafka_notification_topic_messages:
        messages = kafka_notification_topic_messages[topic]
        messages.append(str(gpbmsg.body))
    elif topic in kafka_telemetry_topic_messages:
        messages = kafka_telemetry_topic_messages[topic]
        messages.append(str(gpbmsg.body))

def consume_loop():
    topics =[VOMCI1_REQUEST_TOPIC_NAME, VOMCI1_RESPONSE_TOPIC_NAME, VOMCI1_NOTIFICATION_TOPIC_NAME, VOMCI1_TELEMETRY_TOPIC_NAME,
             VOMCI2_REQUEST_TOPIC_NAME, VOMCI2_RESPONSE_TOPIC_NAME, VOMCI2_NOTIFICATION_TOPIC_NAME, VOMCI2_TELEMETRY_TOPIC_NAME,
             VOMCI3_REQUEST_TOPIC_NAME, VOMCI3_RESPONSE_TOPIC_NAME, VOMCI3_NOTIFICATION_TOPIC_NAME, VOMCI3_TELEMETRY_TOPIC_NAME,
             VPROXY_REQUEST_TOPIC_NAME, VPROXY_RESPONSE_TOPIC_NAME, VPROXY_NOTIFICATION_TOPIC_NAME]
    logger.info("Consuming from topics: %s", topics)
    dummy_msg = Msg()
    for topic in topics:
        producer.produce(topic, key="key", value=bytes(dummy_msg.SerializeToString()), callback=acked)
        producer.flush()
    try:
        consumer.subscribe(topics)
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logger.error('Reached end of offset')
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                process_received_message(msg)
    finally:
        consumer.close()

class MessageData:

    VOMCI_FUNCTION = 'VOMCI_FUNCTION'
    VOMCI_PROXY = 'VOMCI_PROXY'
    ONU = 'ONU'

    VOMCI1_NAME = "vomci-vendor-1"
    VOMCI2_NAME = "vomci-vendor-2"
    VOMCI3_NAME = "vomci-vendor-3"
    VOMCI_PROXY_NAME = "proxy-1"

    ACTION = 'ACTION'
    REPLACE_CONFIG = 'REPLACE_CONFIG'
    UPDATE_CONFIG = 'UPDATE_CONFIG'
    UPDATE_CONFIG_INST = 'UPDATE_CONFIG_INST'
    UPDATE_CONFIG_REPLICA = 'UPDATE_CONFIG_REPLICA'
    GET_DATA = 'GET_DATA'


recipient_name_kafka_request_topic = {
    MessageData.VOMCI1_NAME: VOMCI1_REQUEST_TOPIC_NAME,
    MessageData.VOMCI2_NAME: VOMCI2_REQUEST_TOPIC_NAME,
    MessageData.VOMCI3_NAME: VOMCI3_REQUEST_TOPIC_NAME,
    MessageData.VOMCI_PROXY_NAME: VPROXY_REQUEST_TOPIC_NAME
}

recipient_name_kafka_response_messages = {
    MessageData.VOMCI1_NAME: vomci1_responses,
    MessageData.VOMCI2_NAME: vomci2_responses,
    MessageData.VOMCI3_NAME: vomci3_responses,
    MessageData.VOMCI_PROXY_NAME: vproxy_responses
}

recipient_name_kafka_notification_messages = {
    MessageData.VOMCI1_NAME: vomci1_notifications,
    MessageData.VOMCI2_NAME: vomci2_notifications,
    MessageData.VOMCI3_NAME: vomci3_notifications,
    MessageData.VOMCI_PROXY_NAME: vproxy_notifications
}

kafka_response_topic_messages = {
    VOMCI1_RESPONSE_TOPIC_NAME: vomci1_responses,
    VOMCI2_RESPONSE_TOPIC_NAME: vomci2_responses,
    VOMCI3_RESPONSE_TOPIC_NAME: vomci3_responses,
    VPROXY_RESPONSE_TOPIC_NAME: vproxy_responses,
}

kafka_notification_topic_messages = {
    VOMCI1_NOTIFICATION_TOPIC_NAME: vomci1_notifications,
    VOMCI2_NOTIFICATION_TOPIC_NAME: vomci2_notifications,
    VOMCI3_NOTIFICATION_TOPIC_NAME: vomci3_notifications,
    VPROXY_NOTIFICATION_TOPIC_NAME: vproxy_notifications,
}

kafka_telemetry_topic_messages = {
    VOMCI1_TELEMETRY_TOPIC_NAME: vomci1_telemetry,
    VOMCI2_TELEMETRY_TOPIC_NAME: vomci2_telemetry,
    VOMCI3_TELEMETRY_TOPIC_NAME: vomci3_telemetry,
}

recipient_name_kafka_telemetry_messages = {
    MessageData.VOMCI1_NAME: vomci1_telemetry,
    MessageData.VOMCI2_NAME: vomci2_telemetry,
    MessageData.VOMCI3_NAME: vomci3_telemetry,
}

object_type_header = {
    MessageData.VOMCI_FUNCTION: Msg().header.VOMCI_FUNCTION,
    MessageData.VOMCI_PROXY: Msg().header.VOMCI_PROXY,
    MessageData.ONU: Msg().header.ONU
}