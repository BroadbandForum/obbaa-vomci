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
import omcc.grpc.service_definition.tr451_vomci_sbi_message_pb2 as tr451_vomci_sbi_message_pb2
import omcc.grpc.service_definition.tr451_vomci_sbi_service_pb2_grpc as tr451_vomci_sbi_service_pb2_grpc
from omci_logger import OmciLogger
import os
import grpc
import time
import google.protobuf

LOCAL_GRPC_SERVER_PORT = os.getenv("LOCAL_GRPC_SERVER_PORT")
REMOTE_GRPC_SERVER_PORT = os.getenv("REMOTE_GRPC_SERVER_PORT")
REMOTE_GRPC_SERVER_HOST = os.getenv("REMOTE_GRPC_SERVER_HOST", "localhost")

OmciLogger(level=logging.DEBUG)
logger = OmciLogger.getLogger(__name__)


def main():
    logger.info("Test olt has been started...")
    local_endpoint = tr451_vomci_sbi_message_pb2.Hello(endpoint_name="olt-grpc:1")
    hello_req = tr451_vomci_sbi_message_pb2.HelloVomciRequest(local_endpoint_hello=local_endpoint)
    host = REMOTE_GRPC_SERVER_HOST
    port = REMOTE_GRPC_SERVER_PORT
    connect_to = host + ':' + port
    channel = grpc.insecure_channel(connect_to)
    fail = True
    time.sleep(5)
    while fail:
        try:
            hello_stub = tr451_vomci_sbi_service_pb2_grpc.VomciHelloSbiStub(channel)
            hello_rsp = hello_stub.HelloVomci(hello_req)
            logger.info(hello_rsp.remote_endpoint_hello.endpoint_name)
            message_stub = tr451_vomci_sbi_service_pb2_grpc.VomciMessageSbiStub(channel)
            omci_rx_stream = message_stub.ListenForVomciRx(google.protobuf.empty_pb2.Empty())
            fail = False
        except:
            fail = True
            time.sleep(1)
    for vomci_msg in omci_rx_stream:
        logger.info("test_olt received a message")
        logger.info(vomci_msg)
        packet = vomci_msg.omci_packet_msg
        onu_header = packet.header
        olt_id = onu_header.olt_name
        onu_id = (onu_header.chnl_term_name, onu_header.onu_id)
        msg = b'message received from test olt..............'
        header = tr451_vomci_sbi_message_pb2.OnuHeader(olt_name=olt_id, chnl_term_name=onu_id[0], onu_id=onu_id[1])
        omci_packet = tr451_vomci_sbi_message_pb2.OmciPacket(
            header=header,
            payload=msg)
        message_stub.VomciTx(tr451_vomci_sbi_message_pb2.VomciMessage(omci_packet_msg=omci_packet))
    return


if __name__ == '__main__':
    main()
