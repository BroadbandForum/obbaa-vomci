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

#
# gRPC Client implementation of OltCommChannel class
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" gRPC Communication channel
This module should be implemented properly.
Implementation below is just for testing
"""
import sys
from omci_types import *
from omci_logger import OmciLogger
from omcc.omci_channel import OltCommChannel
import grpc
import google.protobuf
import threading
import omcc.grpc.service_definition.tr451_vomci_function_sbi_message_pb2 as tr451_vomci_function_sbi_message_pb2
import omcc.grpc.service_definition.tr451_vomci_function_sbi_service_pb2_grpc as tr451_vomci_function_sbi_service_pb2_grpc

logger = OmciLogger.getLogger(__name__)


class GrpcChannel(OltCommChannel):
    """ gRPC channel based on service specification in WT-451 working text """
    def __init__(self, name: str, description: str = ''):
        """ Class contructor.

        Args:
            name : vOMCI endpoint name
            description: optional description
        """
        super().__init__(name, description)
        self._channel = None
        self._hello_stub = None
        self._message_stub = None
        self._omci_rx_stream = None
        self._thread = None

    def _thread_function(self):
        logger.info("ListenForOmciRx thread {} started".format(self._name))
        try:
            for packet in self._omci_rx_stream:
                onu_id = (packet.chnl_term_name, int(packet.onu_id))
                self._olt.recv(onu_id, packet.payload)
        except:
            exc_info = sys.exc_info()
            if len(exc_info) > 1 and str(exc_info[1]).find('StatusCode.CANCELLED') >= 0:
                logger.info("{}: gRPC disconnect by user request.".format(self._name))
            else:
                logger.warning("{}: gRPC disconnect. {}".format(self._name, exc_info[0]))
            self._hello_stub = None
            self._message_stub = None
            self._channel = None
            self._omci_rx_stream = None
        logger.info("ListenForOmciRx thread {} terminated".format(self._name))
        self.disconnected()

    def connect(self, host: str, port: int, auth: Optional['Dict'] = None) -> 'Olt':
        """ Connect with pOlt (client mode)).

        Args:
            host: host to connect to
            port: port to connect to
            auth: authentication parameters (TBD)
        Returns:
            True if successful
        """

        hello_req = tr451_vomci_function_sbi_message_pb2.HelloVomciRequest(
            vomci_function = tr451_vomci_function_sbi_message_pb2.VomciFunctionHello(
                vomci_name=self._name))
        try:
            self._channel = grpc.insecure_channel('{}:{}'.format(host, port))
            self._hello_stub = tr451_vomci_function_sbi_service_pb2_grpc.OmciFunctionHelloSbiStub(self._channel)
            self._message_stub = tr451_vomci_function_sbi_service_pb2_grpc.OmciFunctionMessageSbiStub(self._channel)
            # Initiate a Hello handshake
            hello_rsp = self._hello_stub.HelloVomci(hello_req)
            self._omci_rx_stream = self._message_stub.ListenForOmciRx(google.protobuf.empty_pb2.Empty())
        except:
            logger.warning("Failed to connect to {}:{}. Error {}".format(host, port, sys.exc_info()[0]))
            self._hello_stub = None
            self._message_stub = None
            self._channel = None
            self._omci_rx_stream = None
            hello_rsp = None

        if hello_rsp is None:
            return None

        # Create/update OLT object
        olt = self.connected(hello_rsp.olt.olt_name)

        # Create a thread that will listen of OMCI Rx from vOMCI
        self._thread = threading.Thread(name=self._name, target=self._thread_function)
        self._thread.start()
        return olt

    def disconnect(self):
        """ Disconnect from the peer pOlt.
        """
        if self._omci_rx_stream is not None:
            self._omci_rx_stream.cancel()

        if self._thread is not None:
            self._thread.join()
            self._thread = None

        self.disconnected()

    def send(self, onu: 'OnuDriver', msg: RawMessage) -> bool:
        """ Send message to ONU

        Args:
            onu: ONU object
            msg: raw OMCI message without MIC
        Returns:
            True if successful
        """
        if len(msg) != 44:
            logger.error("Invalid message length {}".format(len(msg)))

        try:
            onu_id = onu.onu_id
            omci_packet = tr451_vomci_function_sbi_message_pb2.OmciPacket(
                chnl_term_name=onu_id[0], onu_id=str(onu_id[1]),
                payload=msg)
            self._message_stub.OmciTx(omci_packet)
            ret = True
        except:
            logger.warning("Failed to send to {}:{}. Error {}".format(self._olt.id, onu_id, sys.exc_info()[0]))
            ret = False

        return ret
