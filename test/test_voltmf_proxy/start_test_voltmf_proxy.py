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
from nbi import kafka_interface
import threading, json

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


def main():
    kafka_if = kafka_interface.KafkaInterface(v_omci=None)
    voltmf_thread = threading.Thread(name='kafka_test_voltmf', target=kafka_if.start)
    voltmf_thread.start()
    while kafka_if._producer is None:
        time.sleep(10)
    time.sleep(5)
    logger.info("sending Kafka configuration")
    with open('test/bbf-vomci-proxy.json') as f:
        msg = json.load(f)
    kafka_if.send_msg(msg)

def create_onu_rpc():
    mock_vomci = MockVomci()
    kafka_if = kafka_interface.KafkaInterface(v_omci=mock_vomci)
    voltmf_thread = threading.Thread(name='kafka_test_voltmf', target=kafka_if.start)
    voltmf_thread.start()
    while kafka_if._producer is None:
        time.sleep(10)
    logger.info("sending onu create rpc")
    with open('test/bbf-create-onu2.json') as f:
        msg = json.load(f)
    kafka_if.send_msg(msg['create'])
    time.sleep(5)
    kafka_if.send_msg(msg['set'])
    while True:
        time.sleep(5)

if __name__ == '__main__':
    create_onu_rpc()
