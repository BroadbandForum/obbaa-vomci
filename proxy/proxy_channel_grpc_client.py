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

""" gRPC Communication channel
This module should be implemented properly.
Implementation below is just for testing
"""
import sys
from omci_types import *
from omci_logger import OmciLogger
import grpc
import google.protobuf
import threading
import omcc.grpc.service_definition.tr451_vomci_function_sbi_message_pb2 as tr451_vomci_function_sbi_message_pb2
import omcc.grpc.service_definition.tr451_vomci_function_sbi_service_pb2_grpc \
                                                                        as tr451_vomci_function_sbi_service_pb2_grpc

logger = OmciLogger.getLogger(__name__)


class ProxyGrpcChannel:
    """ gRPC channel based on service specification in WT-451 working text """
    def __init__(self, proxy, name: str):
        """ Class constructor.
        Args:
            proxy: parent Proxy
            name : vOMCI endpoint name
        """
        self._name = name  # Setting up after Hello Message this is the OLT name
        self._channel = None
        self._hello_stub = None
        self._message_stub = None
        self._omci_rx_stream = None
        self._thread = None
        self._parent_proxy = proxy

    def _thread_function_for_proxy(self):
        try:
            for packet in self._omci_rx_stream:
                logger.info("ListenForOmciRx thread received a message: {} ".format(packet))
                onu_id = (packet.chnl_term_name, int(packet.onu_id))
                payload = packet.payload
                self._parent_proxy.on_vomci_message(onu_id, payload)
        except:
            exc_info = sys.exc_info()
            if len(exc_info) > 1 and str(exc_info[1]).find('StatusCode.CANCELLED') >= 0:
                logger.debug("{}: gRPC disconnect by user request.".format(self._name))
            else:
                logger.warning("{}: gRPC disconnect. {}".format(self._name, exc_info[0]))
                self._hello_stub = None
                self._message_stub = None
                self._channel = None
                self._omci_rx_stream = None
        logger.debug("ListenForOmciRx thread {} terminated".format(self._name))

    def connect(self, host: str, port: int, auth: Optional['Dict'] = None):
        hello_req = tr451_vomci_function_sbi_message_pb2.HelloVomciRequest(
            olt=tr451_vomci_function_sbi_message_pb2.OltHello(olt_name=self._name))
        try:
            self._channel = grpc.insecure_channel('{}:{}'.format(host, port))
            self._hello_stub = tr451_vomci_function_sbi_service_pb2_grpc.OmciFunctionHelloSbiStub(self._channel)
            hello_rsp = self._hello_stub.HelloVomci(hello_req)
            logger.debug("Received hello response: {} .Starting OMCI Listener".format(hello_rsp))
            self._message_stub = tr451_vomci_function_sbi_service_pb2_grpc.OmciFunctionMessageSbiStub(self._channel)
            self._omci_rx_stream = self._message_stub.ListenForOmciRx(google.protobuf.empty_pb2.Empty())
        except:
            logger.warning("Failed to connect to {}:{}. Error {}".format(host, port, sys.exc_info()[0]))
            self._hello_stub = None
            self._message_stub = None
            self._channel = None
            self._omci_rx_stream = None
            hello_rsp = None

        if hello_rsp is None:
            logger.error("hello_rsp is empty")
            return None

        # Create/update OLT object
        # olt = self.connected(hello_rsp.vomci_function.omci_name)
        logger.debug("Create a thread that will handle received OMCI messages")
        # Create a thread that will listen of OMCI Rx from vOMCI
        self._thread = threading.Thread(name=self._name, target=self._thread_function_for_proxy)
        self._thread.start()

        return

    def disconnect(self):
        """ Disconnect from the peer pOlt.
        """
        if self._omci_rx_stream is not None:
            self._omci_rx_stream.cancel()

        if self._thread is not None:
            self._thread.join()
            self._thread = None

        # self.disconnected()

    def send(self, onu_id: 'OnuSbiId', msg: RawMessage) -> bool:
        """ Send message to vOMCI
        Args:
            onu_id: OnuSbiId" Tuple[str, int](PonID, TClayerONUid)
            msg: raw OMCI message without MIC
        Returns:
            True if successful
        """
        if len(msg) != 44:
            logger.error("Invalid message length {}".format(len(msg)))
        try:
            omci_packet = tr451_vomci_function_sbi_message_pb2.OmciPacket(
                chnl_term_name=onu_id[0], onu_id=str(onu_id[1]),
                payload=msg)
            self._message_stub.OmciTx(omci_packet)
            ret = True
        except:
            logger.warning("Failed to send package from :{}. Error {}".format(onu_id, sys.exc_info()[0]))
            ret = False
        return ret
