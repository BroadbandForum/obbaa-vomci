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

""" gRPC Server

"""
import google.protobuf
import grpc
import time
import queue
import os
import threading
from concurrent import futures
import omcc.grpc.service_definition.tr451_vomci_sbi_message_pb2 as tr451_vomci_sbi_message_pb2
import omcc.grpc.service_definition.tr451_vomci_sbi_service_pb2_grpc as tr451_vomci_sbi_service_pb2_grpc
from omci_types import *
from omci_logger import OmciLogger
from database.omci_olt import OltDatabase
from omcc.omci_channel import OltCommChannel

logger = OmciLogger.getLogger(__name__)

DEFAULT_GRPC_NAME = "vOMCIProxy"
grpc_vomci_name = os.getenv("GRPC_SERVER_NAME", default=DEFAULT_GRPC_NAME)
if not grpc_vomci_name:
    grpc_vomci_name = DEFAULT_GRPC_NAME


class GrpcServerChannel(OltCommChannel):
    """ gRPC channel based on service specification in WT-451 working text """
    def __init__(self, name: str, server: 'GrpcServer', description: str = '', remote_endpoint=None ):
        super().__init__(name, description)
        self.server = server
        self._context = None
        self.disconnecting = False
        self.omci_msg_queue = queue.Queue()  # packets to be sent to OLT rx_stream single per OLT
        self._remote_endpoint_name = None
        if remote_endpoint is not None:
            self._remote_endpoint_name = remote_endpoint

    @property
    def remote_endpoint_name(self):
        return self._remote_endpoint_name

    @property
    def local_endpoint_name(self):
        return self._name

    def set_context(self, context):
        self._context = context

    def disconnect(self):
        """ Disconnect from the peer pOlt.
        """
        while not self.omci_msg_queue.empty():
            logger.info("Queue was not empty. emptying")
            self.omci_msg_queue.get()
            self.omci_msg_queue.task_done()
        if self._context is not None:
            self.disconnecting = True
            while self._context is not None:
                time.sleep(1)
        self.disconnected()

    def get_olt_name(self):
        if self._olt is None:
            return False
        (olt_name, endpoint_name) = self._olt.id
        return olt_name

    def olt_connection_exists(self, olt_id):
        if self._olt is None:
            return False
        return self._olt.id == (olt_id, self.remote_endpoint_name)

    def get_olt_with_id(self, olt_id):
        if self.olt_connection_exists(olt_id):
            return self._olt
        return None

    def send(self, olt_id, onu_id, msg: RawMessage) -> bool:
        """ Send message to ONU
        Returns:
            True if successful
        """
        if len(msg) != 44:
            logger.error("Invalid message length {}".format(len(msg)))
        if not self.olt_connection_exists(olt_id):
            logger.error("Cannot send message for olt {} in channel with {}".format(olt_id, self.remote_endpoint_name))
            return False
        onu = self._olt.OnuGet(onu_id=onu_id, log_error=False)
        onu_id = onu.onu_id
        header = tr451_vomci_sbi_message_pb2.OnuHeader(olt_name=olt_id, chnl_term_name=onu_id[0], onu_id=onu_id[1])
        omci_packet = tr451_vomci_sbi_message_pb2.OmciPacket(header=header, payload=msg)
        vomci_message = tr451_vomci_sbi_message_pb2.VomciMessage(omci_packet_msg=omci_packet)
        logger.debug("Sending message from ONU {}.{}.{} to {}".format(olt_id, onu_id[0], onu_id[1], self.remote_endpoint_name))
        self.omci_msg_queue.put(vomci_message)
        return True

    def connected(self, olt_id: OltId) -> 'Olt':
        """ Connected indication
        This function is called after successful
        completion of Hello exchange.
        Args:
            olt_id: OLT Id as given by the management chain configuration
        Returns:
            Olt object
        """
        polt_id = (olt_id, self.remote_endpoint_name)
        logger.info("vOMCI {} is connected to pOLT {}".format(self.local_endpoint_name, polt_id))
        if self._olt is None:
            self._olt = OltDatabase().OltAddUpdate(polt_id, self)
        return self._olt

    def add_managed_onu(self, olt_id, onu_name: OnuName, onu_id: OnuSbiId, tci: int = 0):
        """ Add managed onu to self OLT Database
        Args:
            olt_id: Name of OLT
            onu_id: ONU id
            onu_name: ONU name
        """
        if self._olt is None:
            self.connected(olt_id)
        if not self.olt_connection_exists(olt_id):
            return None
        self._olt.OnuAddUpdate(onu_name, onu_id, tci)
        logger.info("Managed ONU {}:{} was added to pOLT {} ".format(onu_name, onu_id, self._olt.id))
        return self._olt

    def recv(self, vomci_msg : tr451_vomci_sbi_message_pb2):
        packet = vomci_msg.omci_packet_msg
        if packet is None:
            logger.error("Message from {} is not a packet".format(
                self._context and self._context.peer() or '?'))
            return
        onu_header = packet.header
        onu_id = (onu_header.chnl_term_name, onu_header.onu_id)
        logger.debug("Sending message from {} to ONU {}.{}.{}".format(self.remote_endpoint_name, self._olt, onu_id[0], onu_id[1]))
        payload = packet.payload
        if self._olt is not None:
            self._olt.recv(onu_id, payload)


class GrpcServer:
    """ gRPC server. Listens for new connections """
    def __init__(self, port, name=None, connection_type=GrpcServerChannel, parent=None):
        """ Class constructor.

        Args:
            port : port to listen on for new connections
            name : server name
            connection_type : class used to create new connections
        """
        self._name = name and name or grpc_vomci_name
        self._port = port
        self._hello_servicer = OmciChannelHelloServicer(self)
        self._message_servicer = OmciChannelMessageServicer(self)
        self._server = None  # server that host the two servicers
        self._thread = None  # Tread that runs the server
        self._connections = {}  # this is a dict that includes all the GrpcChannels
        self._connection_type = connection_type
        self._parent = None
        if parent is not None:
            self._parent = parent
        self._start()

    def __del__(self):
        self.stop()

    @property
    def name(self):
        return self._name

    @property
    def connection_type(self):
        return self._connection_type

    def _server_routine(self):
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        tr451_vomci_sbi_service_pb2_grpc.add_VomciHelloSbiServicer_to_server(self._hello_servicer, self._server)
        tr451_vomci_sbi_service_pb2_grpc.add_VomciMessageSbiServicer_to_server(self._message_servicer, self._server)
        self._server.add_insecure_port('0.0.0.0:' + str(self._port))

        self._server.start()
        logger.debug("gRPC server is waiting for connections")
        self._server.wait_for_termination()
        self._server = None
        self._thread = None

    def _start(self):
        if self._thread is None:
            logger.info("Starting gRPC server")
            self._thread = threading.Thread(name=self._name, target=self._server_routine)
            self._thread.start()
        else:
            logger.debug("gRPC Server already exists")
        time.sleep(2)

    def connections(self):
        return self._connections

    def connection_get(self, peer: str):
        if peer in self._connections:
            return self._connections[peer]
        return None

    def connection_add(self, peer: str, channel : OltCommChannel):
        self._connections[peer] = channel

    def connection_delete(self, peer: str):
        if peer in self._connections:
            del self._connections[peer]

    def stop(self):
        if self._server is not None:
            self._server.stop(True)
        conns_list = list(self._connections.values())
        for _conn in conns_list:
            _conn.disconnect()

    def create_connection(self, remote_endpoint_name, peer):
        """ Iterate over connection and check if connection with the
            same remote_endpoint_name already exists. If does exist - it is stale
            and need to be replaced. If it doesn't, create a new one
        """
        channel = None
        for _peer, _conn in self._connections.items():
            if _conn.name == remote_endpoint_name:
                self.connection_delete(_peer)
                channel = _conn
                break
        if channel is None:
            channel = self._connection_type(server=self, name=self._name, description=peer, remote_endpoint=remote_endpoint_name)
        self.connection_add(peer, channel)
        if self._parent is not None:
            self._parent.add_managed_onus(channel)

    def send(self, olt_id, onu_id: OnuSbiId, msg: RawMessage):
        """ Send message to the right connection according the olt_id
        Args:
            olt_id: name of OLT
            onu_id: OnuSbiId object
            msg: raw OMCI message without MIC
        Returns:
            True if successful
        """
        conn = None
        for peer in self._connections.keys():
            if self._connections[peer].olt_connection_exists(olt_id):
                conn = self._connections[peer]
                break
        if conn is None:
            logger.error("GrpcServer: connection for OLT {} not found".format(olt_id))
            return False
        else:
            return conn.send(olt_id, onu_id, msg)


class OmciChannelHelloServicer(tr451_vomci_sbi_service_pb2_grpc.VomciHelloSbiServicer):
    """Provides methods that implement the Hello Sbi Server"""

    def __init__(self, grpc_server: GrpcServer):
        self._name = grpc_server.name
        self._server = grpc_server

    def HelloVomci(self, request, context):
        """ rpc to be called - Session establishment"""
        remote_endpoint_name = request.local_endpoint_hello.endpoint_name
        peer = context.peer()
        logger.info("vOMCI {} received hello from {} at {}".format(self._name, remote_endpoint_name, peer))
        self._server.create_connection(remote_endpoint_name, peer)
        hello_resp = tr451_vomci_sbi_message_pb2.HelloVomciResponse(
            remote_endpoint_hello=tr451_vomci_sbi_message_pb2.Hello(
                endpoint_name=self._name))
        return hello_resp


class OmciChannelMessageServicer(tr451_vomci_sbi_service_pb2_grpc.VomciMessageSbiServicer):
    """Provides methods that implement the Message Sbi Server"""

    def __init__(self, grpc_server):
        self._server = grpc_server

    def VomciTx(self, request, context):
        """ rpc to be called - OMCI msgs from pOLT --> vOMCI """
        peer = context.peer()
        channel = self._server.connection_get(peer)
        if channel is None:
            logger.error("Message received from unknown source {}".format(context.peer()))
            return google.protobuf.empty_pb2.Empty()

        channel.recv(request)
        return google.protobuf.empty_pb2.Empty()

    def ListenForVomciRx(self, request, context):
        """ rpc to be called - OMCI msgs from vOMCI --> pOLT"""
        peer = context.peer()
        channel = self._server.connection_get(peer)
        if channel:
            channel.set_context(context)
            while context.is_active and not channel.disconnecting:
                try:
                    message = channel.omci_msg_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                channel.omci_msg_queue.task_done()
                yield message
            logger.info("ListenForVomciRx from {} at {} was cancelled :".format(channel.name, peer))
            channel.set_context(None)
            channel.disconnect()
            self._server.connection_delete(peer)

        else:
            logger.error("Message received from unknown source {}".format(peer))
        return google.protobuf.empty_pb2.Empty()
