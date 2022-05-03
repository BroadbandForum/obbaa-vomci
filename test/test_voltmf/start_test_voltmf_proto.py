# Copyright 2020 Broadband Forum
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

import logging
from omci_logger import OmciLogger
import os
import time
from nbi import kafka_proto_interface
import threading, json
from proto_messages_vomci import getSampleProtoVomci as getSampleProto

LOCAL_GRPC_SERVER_PORT = os.getenv("LOCAL_GRPC_SERVER_PORT")
REMOTE_GRPC_SERVER_PORT = os.getenv("REMOTE_GRPC_SERVER_PORT")
REMOTE_GRPC_SERVER_HOST = os.getenv("REMOTE_GRPC_SERVER_HOST", "localhost")

OmciLogger(level=logging.DEBUG)
logger = OmciLogger.getLogger(__name__)

class MockVomci:
    def trigger_create_onu(self, name):
        pass

    def trigger_set_onu_communication(self, olt_name: str, onu_name: str, channel_termination: str,
                                      onu_tc_id: int, available: bool, olt_endpoint_name: str, voltmf_endpoint_name: str):
        pass

def management_chain():
    mock_vomci = MockVomci()
    kafka_if = kafka_proto_interface.KafkaProtoInterface(v_omci=mock_vomci)
    voltmf_thread = threading.Thread(name='kafka_test_voltmf1', target=kafka_if.start)
    voltmf_thread.start()
    while kafka_if._producer is None:
        time.sleep(10)
    logger.info("sending Kafka configuration")
    with open('test/bbf-vomci-function.json') as f:
        msg = json.load(f)
    kafka_if._producer.send_proto_response(msg)

def create_onu_rpc():
    mock_vomci = MockVomci()
    kafka_if = kafka_proto_interface.KafkaProtoInterface('mock1', v_omci=mock_vomci)
    voltmf_thread = threading.Thread(name='kafka_test_voltmf1', target=kafka_if.start)
    voltmf_thread.start()
    while kafka_if._producer is None:
        time.sleep(10)
    
    kafka_if._producer.set_topics(['OBBAA_ONU_REQUEST'])
    kafka_if._consumer.set_topics(['vomci1-response', 'vomci1-notification'])

    logger.info("Sending hello request")
    kafka_if._producer.send_proto_response(getSampleProto('hello'))
    time.sleep(5)
    logger.info("sending update config action")
    kafka_if._producer.send_proto_response(getSampleProto('update_config'))
    time.sleep(10)

    kafka_if._producer.set_topics(['vomci1-request'])

    logger.info("sending onu create action")
    kafka_if._producer.send_proto_response(getSampleProto('create'))
    time.sleep(5)
    logger.info("sending onu set action")
    kafka_if._producer.send_proto_response(getSampleProto('set'))
    while True:
        time.sleep(5)
    # kafka_if.send_msg(msg['create1'])
    # time.sleep(5)
    # kafka_if.send_msg(msg['set1'])
    # time.sleep(540)
    # kafka_if.send_msg(msg['unset1'])

if __name__ == '__main__':
    create_onu_rpc()
