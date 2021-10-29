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
from database.omci_olt import OltDatabase
import grpc
import google.protobuf
import threading, time
import omcc.grpc.service_definition.tr451_vomci_sbi_message_pb2 as tr451_vomci_sbi_message_pb2
import omcc.grpc.service_definition.tr451_vomci_sbi_service_pb2_grpc as tr451_vomci_sbi_service_pb2_grpc

logger = OmciLogger.getLogger(__name__)


class GrpcClientChannel(OltCommChannel):
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
        self._remote_endpoint_name = None
        self._olts = dict()

    def get_olt_with_id(self, olt_id) -> bool:
        return self._olts.get(olt_id)

    def olt_connection_exists(self, olt_id):
        return self._olts.get(olt_id) is not None

    @property
    def remote_endpoint_name(self):
        return self._remote_endpoint_name

    @property
    def local_endpoint_name(self):
        return self._name

    def connect(self, host: str, port: int, auth: Optional['Dict'] = None, retry=False) -> bool :
        """ Connect with peer entity (client mode)).

        Args:
            host: host to connect to
            port: port to connect to
            auth: authentication parameters (TBD)
            retry: retry if connect fails
        Returns:
            True if successful
            False otherwise
        """

        local_endpoint = tr451_vomci_sbi_message_pb2.Hello(endpoint_name=self._name)
        hello_req = tr451_vomci_sbi_message_pb2.HelloVomciRequest(local_endpoint_hello=local_endpoint)
        fail = True
        while fail:
            try:
                self._channel = grpc.insecure_channel('{}:{}'.format(host, port))
                self._hello_stub = tr451_vomci_sbi_service_pb2_grpc.VomciHelloSbiStub(self._channel)
                self._message_stub = tr451_vomci_sbi_service_pb2_grpc.VomciMessageSbiStub(self._channel)
                # Initiate a Hello handshake
                hello_rsp = self._hello_stub.HelloVomci(hello_req)
                self._omci_rx_stream = self._message_stub.ListenForVomciRx(google.protobuf.empty_pb2.Empty())
                fail = False
            except:
                logger.warning("Failed to connect to {}:{}. Error {}".format(host, port, sys.exc_info()[0]))
                self._hello_stub = None
                self._message_stub = None
                self._channel = None
                self._omci_rx_stream = None
                hello_rsp = None
                if retry:
                    logger.warning("Retrying to connect to {}:{} in 5s".format(host, port))
                    fail = True
                    time.sleep(5)
                else:
                    fail = False

        if hello_rsp is None:
            return False

        self._remote_endpoint_name = hello_rsp.remote_endpoint_hello.endpoint_name
        logger.info("{} connected to {}".format(self._name, self._remote_endpoint_name))
        # Create a thread that will listen of OMCI Rx from vOMCI
        self._thread = threading.Thread(name=self._name, target=self._thread_function)
        self._thread.start()
        return True

    def disconnect(self):
        """ Disconnect from peer entity.
        """
        if self._omci_rx_stream is not None:
            self._omci_rx_stream.cancel()

        if self._thread is not None:
            self._thread.join()
            self._thread = None
        self.disconnected()

    def recv(self, vomci_msg : tr451_vomci_sbi_message_pb2):
        packet = vomci_msg.omci_packet_msg
        onu_header = packet.header
        olt_id = onu_header.olt_name
        olt = self.get_olt_with_id(olt_id)
        if olt is None:
            logger.error("Failed while receiving message from {} for olt {}. OLT connection not found".format(
                self.remote_endpoint_name, olt_id))
            return
        onu_id = (onu_header.chnl_term_name, onu_header.onu_id)
        logger.info("GrpcClient: Received message {} from OLT {}".format(packet.payload, olt.id))
        olt.recv(onu_id, packet.payload)

    def send(self, olt_id, onu_id: OnuSbiId, msg: RawMessage) -> bool:
        """ Send message to ONU
        Returns:
            True if successful
        """
        logger.info("GrpcClient: Sending message {} to OLT {}".format(msg, olt_id))
        if len(msg) != 44:
            logger.error("Invalid message length {}".format(len(msg)))
            return False
        if not self.olt_connection_exists(olt_id):
            logger.warning("GrpcClient: wrong channel for {}".format(olt_id))
            return False
        olt = self.get_olt_with_id(olt_id)
        onu = olt.OnuGet(onu_id=onu_id, log_error=False)
        if onu is None:
            logger.warning("GrpcClient: connection for ONU {} not found".format(onu_id))
            return False
        onu_id = onu.onu_id
        try:
            header = tr451_vomci_sbi_message_pb2.OnuHeader(olt_name=olt_id, chnl_term_name=onu_id[0], onu_id=onu_id[1])
            omci_packet = tr451_vomci_sbi_message_pb2.OmciPacket(
                header=header,
                payload=msg)
            self._message_stub.VomciTx(tr451_vomci_sbi_message_pb2.VomciMessage(omci_packet_msg=omci_packet))
            ret = True
        except:
            logger.warning("Failed to send to {}:{}. Error {}".format(olt.id, onu_id, sys.exc_info()[0]))
            ret = False
        return ret

    def connected(self, olt_id: OltId) -> 'Olt':
        """ Connected indication
        This function is called after successful
        completion of Hello exchange.

        Args:
            olt_id: OLT Id as given by the management chain configuration
        Returns:
            Olt object
        """
        if not self.olt_connection_exists(olt_id):
            polt_id = (olt_id, self.remote_endpoint_name)
            logger.info("vOMCI {} is connected to pOLT {}".format(self._name, polt_id))
            self._olts[olt_id] = OltDatabase().OltAddUpdate(polt_id, self)
        return self._olts[olt_id]

    def disconnected(self):
        """ Disconnected indication
        """
        if self._olts is None:
            return
        for olt_id in self._olts.keys():
            polt_id = (olt_id, self.remote_endpoint_name)
            logger.info("vOMCI {} disconnected from pOLT {}".format(self._name, polt_id))
            self._olts[olt_id].set_channel(None)
            OltDatabase().OltDelete(polt_id)
            self._olts[olt_id] = None
        self._olts = dict()

    def add_managed_onu(self, olt_id, onu_name: OnuName, onu_id: OnuSbiId, tci: int = 0):
        """ Add managed onu to self OLT Database
        Args:
            olt_id: Name of OLT
            onu_id: ONU id
            onu_name: ONU name
        """
        olt = self.connected(olt_id)
        olt.OnuAddUpdate(onu_name, onu_id, tci)
        logger.info("Managed ONU {}:{} was added to pOLT {}".format(onu_name, onu_id, olt.id))
        return olt

    def _thread_function(self):
        logger.info("ListenForVomciRx thread {} started".format(self._name))
        try:
            for vomci_msg in self._omci_rx_stream:
                self.recv(vomci_msg)
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
        logger.info("ListenForVomciRx thread {} terminated".format(self._name))
        self.disconnected()
