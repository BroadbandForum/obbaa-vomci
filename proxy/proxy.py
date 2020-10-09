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
from nbi import kafka_interface
from omci_logger import OmciLogger
import proxy.proxy_channel_grpc_client as proxy_grpc_channel
import proxy.proxy_channel_grpc_server as grpc_server
# from database.omci_olt import *
import os
import threading

DEFAULT_BOOTSTRAP_SERVERS = kafka_interface.DEFAULT_BOOTSTRAP_SERVERS
logger = OmciLogger.getLogger(__name__)
VOMCI_GRPC_SERVER = True
# LOCAL_GRPC_SERVER_PORT = 8433
LOCAL_GRPC_SERVER_PORT = os.getenv("LOCAL_GRPC_SERVER_PORT", default=8433)
# LOCAL_GRPC_SERVER_PORT = 58433
REMOTE_GRPC_SERVER_PORT = os.getenv("REMOTE_GRPC_SERVER_PORT", default=8433)
REMOTE_GRPC_SERVER_ADDR = os.getenv("REMOTE_GRPC_SERVER_ADDR", default='obbaa-vomci_vomci_1')


class Proxy:
    def __init__(self, name):
        self._name = name
        self._key_map = {}
        self._server = grpc_server.GrpcServer(self, port=LOCAL_GRPC_SERVER_PORT)
        self._client = None

    def create_vomci_connection(self) -> None:
        host = REMOTE_GRPC_SERVER_ADDR
        port = REMOTE_GRPC_SERVER_PORT
        logger.info("connecting to {}:{}..".format(host, port))
        self._client = proxy_grpc_channel.ProxyGrpcChannel(self, name=self._name)
        self._client.connect(host=host, port=port)
        logger.info("Test {}: connected".format(self._name))
        return

    def create_polt_connection_server(self):
        self._server.create_listen_endpoint()

    def on_hello_message(self, olt_id):
        grpc_client_thread = threading.Thread(name="grpc_client", target=self.create_vomci_connection)
        self._name = olt_id
        grpc_client_thread.start()

    def on_olt_message(self, onu_id, payload):
        self._client.send(onu_id, payload)

    def on_vomci_message(self, onu_id, payload):
        if self._server.pOlt_Connection is None:
            logger.debug("Simulating")
        else:
            self._server.pOlt_Connection.send(onu_id, payload)
