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
from concurrent import futures
from omci_types import *
from omci_logger import OmciLogger
import google.protobuf
import grpc
import time
import queue
import os
import threading
import omcc.grpc.service_definition.tr451_vomci_function_sbi_message_pb2 as tr451_vomci_function_sbi_message_pb2
import \
    omcc.grpc.service_definition.tr451_vomci_function_sbi_service_pb2_grpc as tr451_vomci_function_sbi_service_pb2_grpc

logger = OmciLogger.getLogger(__name__)

DEFAULT_GRPC_NAME = "vOMCIProxy"
grpc_vomci_name = os.getenv("GRPC_SERVER_NAME", default=DEFAULT_GRPC_NAME)
if not grpc_vomci_name:
    grpc_vomci_name = DEFAULT_GRPC_NAME


class CommonGrpcServer:
    def __init__(self, port):
        self._hello_servicer = OmciChannelHelloServicer(self)
        self._message_servicer = OmciChannelMessageServicer(self)
        self._server = None  # server that host the two servicers
        self._thread = None  # Tread that runs the server
        self._name = "GrpcServer"
        self._port = port
        # self._serving_routine = self._serve_routine()
       
    def _server_routine(self):
        self._server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        tr451_vomci_function_sbi_service_pb2_grpc.add_OmciFunctionHelloSbiServicer_to_server(self._hello_servicer,
                                                                                             self._server)
        tr451_vomci_function_sbi_service_pb2_grpc.add_OmciFunctionMessageSbiServicer_to_server(self._message_servicer,
                                                                                               self._server)
        self._server.add_insecure_port('0.0.0.0:' + str(self._port))

        self._server.start()
        logger.debug("gRPC server is waiting for connections")
        self._server.wait_for_termination()

    def create_listen_endpoint(self):
        if self._thread is None:
            logger.info("Starting gRPC server")
            self._thread = threading.Thread(name=self._name, target=self._server_routine)
            self._thread.start()
        else:
            logger.debug("gRPC Server already exists")
        time.sleep(2)

    def handle_hello_msg(self, olt_id, peer):
        logger.warning("DUMMY Function")
        pass

    def peer_exists(self, peer):
        logger.warning("DUMMY Function")
        return True

    def handle_Tx_message(self, onu_id, payload, peer):
        logger.warning("DUMMY Function")
        pass

    def get_connection(self, peer):
        logger.warning("DUMMY Function")
        return None

    def remove_connection(self, peer):
        logger.warning("DUMMY Function")
        pass


class OmciChannelHelloServicer(tr451_vomci_function_sbi_service_pb2_grpc.OmciFunctionHelloSbiServicer):
    """Provides methods that implement the Hello Sbi Server"""

    def __init__(self, grpc_server: CommonGrpcServer):
        self._name = grpc_vomci_name
        self._parent_server = grpc_server

    def HelloVomci(self, request, context):
        """ rpc to be called - Session establishment"""
        olt_id = request.olt.olt_name
        logger.info("vOMCI {} received hello from OLT {} at {}".format(self._name, olt_id, context.peer()))
        peer = context.peer()
        self._parent_server.handle_hello_msg(olt_id, peer)
        hello_resp = tr451_vomci_function_sbi_message_pb2.HelloVomciResponse(
            vomci_function=tr451_vomci_function_sbi_message_pb2.VomciFunctionHello(
                vomci_name=self._name))
        return hello_resp


class OmciChannelMessageServicer(tr451_vomci_function_sbi_service_pb2_grpc.OmciFunctionMessageSbiServicer):
    """Provides methods that implement the Message Sbi Server"""

    def __init__(self, grpc_server):
        self._parent_server = grpc_server

    def OmciTx(self, request, context):
        """ rpc to be called - OMCI msgs from pOLT --> vOMCI """
        peer = context.peer()
        if self._parent_server.peer_exists(peer):
            onu_id = (request.chnl_term_name, int(request.onu_id))
            payload = request.payload
            # TODO check for a possible race condition https://code.broadband-forum.org/projects/OBBAA/repos/obbaa-vomci/pull-requests/16/overview?commentId=9634
            self._parent_server.handle_Tx_message(onu_id, payload, peer)

        else:
            logger.error("Message received from unknown source {}".format(context.peer()))
        return google.protobuf.empty_pb2.Empty()

    def ListenForOmciRx(self, request, context):
        """ rpc to be called - OMCI msgs from vOMCI --> pOLT"""
        peer = context.peer()
        channel = self._parent_server.get_connection(peer)
        if channel:
            channel._connect_action()
            logger.info("vOMCI {} connected with at {}".format(grpc_vomci_name, peer))
            while context.is_active:
                try:
                    packet = channel.omci_msg_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                channel.omci_msg_queue.task_done()
                yield packet
            logger.error("ListenRx Function{} as {} was cancelled :".format(peer, channel.name))
            channel.disconnect()
            self._parent_server.remove_connection(peer)

        else:
            logger.error("Message received from unknown source {}".format(peer))
        return google.protobuf.empty_pb2.Empty()

class CommonGrpcChannel:
    """ gRPC channel based on service specification in WT-451 working text """

    def __init__(self, grpc_server):
        """ Class constructor.
        Args:
            grpc_server: parent GrpcServer
        """
        self._parent_server = grpc_server
        self.omci_msg_queue = queue.Queue()  # packets to be sent to OLT rx_stream single per OLT

    def _disconnect_action(self):
        logger.debug("Dummy Implementation")
        pass

    def _connect_action(self):
        logger.debug("Dummy Implementation")
        pass

    def disconnect(self):
        """ Disconnect from the peer pOlt.
        """
        while not self.omci_msg_queue.empty():
            logger.info("Queue was not empty. emptying")
            self.omci_msg_queue.get()
            self.omci_msg_queue.task_done()
        self._parent_server = None
        self.omci_msg_queue = None
        self._disconnect_action()

    def put_msg_in_queue(self, onu_id, msg):
        if len(msg) != 44:
            logger.error("Invalid message length {}".format(len(msg)))
        omci_packet = tr451_vomci_function_sbi_message_pb2.OmciPacket(chnl_term_name=onu_id[0],
                                                                      onu_id=str(onu_id[1]), payload=msg)
        self.omci_msg_queue.put(omci_packet)