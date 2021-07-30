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
from enum import Enum, auto
# from nbi import kafka_interface
from nbi import kafka_proto_interface as kafka_interface
from omci_logger import OmciLogger
from omcc.omci_channel import OltCommChannel
from omcc.grpc.grpc_server import GrpcServer
import omcc.grpc.service_definition.tr451_vomci_sbi_message_pb2 as tr451_vomci_sbi_message_pb2
import nbi.grpc.service_definition.tr451_vomci_nbi_message_pb2 as tr451_vomci_nbi_message_pb2
import nbi.grpc.service_definition.tr451_vomci_nbi_service_pb2 as tr451_vomci_nbi_service_pb2
from omci_types import RawMessage, OnuSbiId
from database.onu_management_chain import ManagementChain
from database.omci_olt import OltDatabase
import os, threading, time

DEFAULT_BOOTSTRAP_SERVERS = kafka_interface.DEFAULT_BOOTSTRAP_SERVERS
logger = OmciLogger.getLogger(__name__)
VOMCI_GRPC_SERVER = True
LOCAL_GRPC_SERVER_PORT = os.getenv("LOCAL_GRPC_SERVER_PORT", default=8433)
REMOTE_GRPC_SERVER_PORT = os.getenv("REMOTE_GRPC_SERVER_PORT", default=58433)
REMOTE_GRPC_SERVER_ADDR = os.getenv("REMOTE_GRPC_SERVER_ADDR", default='obbaa-vomci_vomci_1')
DEFAULT_GRPC_NAME = "obbaa-vproxy"
vproxy_default_name = os.getenv("GRPC_SERVER_NAME", default=DEFAULT_GRPC_NAME)
grpc_vproxy_client_name = os.getenv("GRPC_CLIENT_NAME", default=DEFAULT_GRPC_NAME)

class ProxyChannelDirection(Enum):
    Upstream = auto()
    Downstream = auto()


import proxy.proxy_channel_grpc_client as proxy_grpc_channel
from proxy.proxy_channel_grpc_server import GrpcProxyServer



class Proxy:
    def __init__(self, name=None):
        self._name = name and name or vproxy_default_name
        self._client_endpoint_name = grpc_vproxy_client_name
        self._server_endpoint_name = self._name
        self._key_map = {}
        self._server = None
        self._upstream_conn = dict()  # contains all upstream client connections
        self._downstream_conn = dict()  # contains all downstream client connections
        self._kafka_thread = None
        self._kafka_if = None

    def start(self):
        logger.info("Starting vomci proxy")
        self._kafka_if = kafka_interface.KafkaProtoInterface(self)
        self._kafka_thread = threading.Thread(name='kafka_vomci_thread', target=self._kafka_if.start)
        self._kafka_thread.start()
        self._start_grpc_server()
        self._create_vomci_connection()

    def trigger_create_onu(self, onu_name):
        """
        Add ONU with onu_name to management chain.
        To be called by the kafka interface when a
        "create ONU" request is received.
        Args:
            onu_name: unique name of ONU
        """
        if ManagementChain.GetOnu(onu_name) is not None:
            er_string = "ONU {} already exists in the management chain".format(onu_name)
            logger.error(er_string)
            self._kafka_if.send_unsuccessful_response(onu_name, error_msg=er_string)
            return
        ManagementChain.CreateOnu(onu_name)
        self._kafka_if.send_successful_response(onu_name)

    def trigger_set_onu_communication(self, olt_name: str, onu_name: str, channel_termination: str,
                                      onu_tc_id: int, available: bool, olt_endpoint_name: str,
                                      vomci_endpoint_name: str, voltmf_name: str):
        """
        Use arguments to set the communication points and management chain
        of given ONU. Then initiate the ONU detect sequence. To be called by
        the kafka interface when a "set ONU communication" request is received.
        """
        if ManagementChain.IsOnuConfigured(onu_name):
            ManagementChain.SetOnuCommunication(olt_name, onu_name, channel_termination,
                                                onu_tc_id, available, olt_endpoint_name, vomci_endpoint_name, voltmf_name)
            self._kafka_if.send_successful_response(onu_name)
        else:
            managed_onu = ManagementChain.SetOnuCommunication(olt_name, onu_name, channel_termination,
                                                              onu_tc_id, available, olt_endpoint_name, vomci_endpoint_name, voltmf_name)
            onu_id = (managed_onu.ct_ref, managed_onu.onu_id)
            for remote_endpoint in self._upstream_conn.keys():
                if managed_onu.upstream_endpoint_name == remote_endpoint:
                    self._upstream_conn[remote_endpoint].add_managed_onu(managed_onu.olt_name, onu_name, onu_id)
                    break
            for remote_endpoint in self._downstream_conn.keys():
                if managed_onu.downstream_endpoint_name == remote_endpoint:
                    self._downstream_conn[remote_endpoint].add_managed_onu(managed_onu.olt_name, onu_name, onu_id)
                    break
            for connection in self._server.connections().values():
                if managed_onu.downstream_endpoint_name == connection.remote_endpoint_name:
                    connection.add_managed_onu(managed_onu.olt_name, onu_name, onu_id)
                    break
            self._kafka_if.send_successful_response(onu_name)

    def trigger_delete_onu(self, onu_name: str):
        managed_onu = ManagementChain.DeleteOnu(onu_name)
        if managed_onu is None:
            logger.warning("Cannot delete ONU {} that has not been created".format(onu_name))
            self._kafka_if.send_unsuccessful_response(onu_name)
            return
        self._delete_onu_from_olt(onu_name, managed_onu.olt_name, managed_onu.downstream_endpoint_name)
        self._delete_onu_from_olt(onu_name, managed_onu.olt_name, managed_onu.upstream_endpoint_name)
        self._kafka_if.send_successful_response(onu_name)

    @staticmethod
    def _delete_onu_from_olt(onu_name, olt_name, endpoint_name):
        olt = OltDatabase.OltGet((olt_name, endpoint_name))
        if olt is None:
            logger.warning("OLT {} with {} has not been connected yet".format(endpoint_name, onu_name))
            return False
        if olt.OnuGetByName(onu_name, False) is not None:
            olt.OnuDelete(onu_name)
            logger.info("ONU {}:{} deleted from the database".format(onu_name, olt.channel.remote_endpoint_name))

    def add_managed_onus(self, comm_channel):
        """
        Add managed onus to communication channel, as per configuration.
        This function should be called by the GrpcServer when
        a new client connection is requested, or by the proxy when a
        new client connection is initiated.
        """
        remote_endpoint_name = comm_channel.remote_endpoint_name
        for managed_onu in ManagementChain.GetManagedOnus():
            if managed_onu.downstream_endpoint_name == remote_endpoint_name or managed_onu.upstream_endpoint_name == remote_endpoint_name:
                onu_id = (managed_onu.ct_ref, managed_onu.onu_id)
                comm_channel.add_managed_onu(managed_onu.olt_name, managed_onu.onu_name, onu_id)

    def _start_grpc_client(self, direction, host, port):
        logger.info("connecting to {}:{}..".format(host, port))
        client = proxy_grpc_channel.ProxyGrpcChannel(self, direction=direction, name=self._client_endpoint_name)
        ret_val = client.connect(host=host, port=port, retry=True)
        if not ret_val:
            logger.info("{}: unable to connect to {}:{}".format(self._client_endpoint_name, host, port))
            return
        self.add_managed_onus(client)
        logger.info("{}: connected to {}:{}".format(self._client_endpoint_name, host, port))
        return client

    def _start_grpc_server(self):
        self._server = GrpcProxyServer(name=self._server_endpoint_name, parent=self, port=LOCAL_GRPC_SERVER_PORT)

    def _create_vomci_connection(self) -> None:
        """
        Initiate a client grpc connection towards the vomci.
        """
        host = REMOTE_GRPC_SERVER_ADDR
        port = REMOTE_GRPC_SERVER_PORT
        logger.info("proxy client {}: Initiating connection with vomci at {}:{}".format(grpc_vproxy_client_name, host, port))
        client = self._start_grpc_client(direction=ProxyChannelDirection.Upstream, host=host, port=port)
        self._upstream_conn[client.remote_endpoint_name] = client
        return

    def _create_olt_connection(self, host, port) -> None:
        """
        Initiate a client grpc connection towards the olt.
        Args:
            host: grpc host address of olt
            port: grpc host port of olt
        """
        client = self._start_grpc_client(direction=ProxyChannelDirection.Downstream, host=host, port=port)
        self._downstream_conn[client.remote_endpoint_name] = client
        return

    def _send_downstream(self, olt_id, onu_id: OnuSbiId, msg: RawMessage):
        """ Message received upstream of the proxy.
            Forward it to be sent from the server,
            or the downstream clients
        Args:
            olt_id: name of OLT
            onu_id: OnuSbiId object
            msg: raw OMCI message without MIC
        Returns:
            True if successful
        """
        if self._server.send(olt_id, onu_id, msg):
            return True
        else:
            return self.send_to_conn(self._downstream_conn, olt_id, onu_id, msg)

    def _send_upstream(self, olt_id, onu_id: OnuSbiId, msg: RawMessage):
        """ Message received downstream of the proxy.
            Forward it to the appropriate upstream client connection
            according the olt_id
        Args:
            olt_id: name of OLT
            onu_id: OnuSbiId object
            msg: raw OMCI message without MIC
        Returns:
            True if successful
        """
        return self.send_to_conn(self._upstream_conn, olt_id, onu_id, msg)

    def recv(self, from_channel: OltCommChannel, vomci_msg: tr451_vomci_sbi_message_pb2):
        """ Examine from_channel.direction, find the opposing
            'to' channel by onu_id and olt_id and forward the message """
        packet = vomci_msg.omci_packet_msg
        if from_channel.direction is ProxyChannelDirection.Upstream:
            logger.info("Received Message from Upstream:{}".format(packet))
        if from_channel.direction is ProxyChannelDirection.Downstream:
            logger.info("Received Message from Downstream:{}".format(packet))
        if packet is None:
            # This is an OmciError message
            # TODO: add handling
            return
        onu_header = packet.header
        onu_id = (onu_header.chnl_term_name, onu_header.onu_id)
        if from_channel.direction is ProxyChannelDirection.Downstream:
            olt_id = from_channel.get_olt_name()
        else:
            olt_id = onu_header.olt_name
        payload = packet.payload
        logger.info("Message received {} for OLT {}".format(packet.payload, olt_id))
        if from_channel.direction is ProxyChannelDirection.Upstream:  # message received from vomci
            return self._send_downstream(olt_id, onu_id, payload)
        elif from_channel.direction is ProxyChannelDirection.Downstream:  # message received from olt
            return self._send_upstream(olt_id, onu_id, payload)

    @staticmethod
    def send_to_conn(conn_dict, olt_id, onu_id, msg):
        conn = None
        logger.info('Packet received from the OLT:{} for ONU:{}'.format(olt_id,onu_id))
        for host in conn_dict.keys():
            if conn_dict[host].olt_connection_exists(olt_id):
                conn = conn_dict[host]
                break
        if conn is None:
            logger.error("Connection for OLT {} not found".format(olt_id))
            return False
        else:
            return conn.send(olt_id, onu_id, msg)
