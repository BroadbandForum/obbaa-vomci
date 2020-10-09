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

from omci_types import *
from omci_logger import OmciLogger
from omcc.grpc.grpc_server_common import CommonGrpcServer, CommonGrpcChannel
logger = OmciLogger.getLogger(__name__)

DEFAULT_GRPC_NAME = "vOMCIProxy"


class GrpcServer(CommonGrpcServer):
    def __init__(self, parent_proxy, port):
        super().__init__(port)
        self.proxy = parent_proxy
        self.pOlt_Connection = None  # this is a dict that includes all the GrpcChannels
        self.olt_peer = None

    def handle_hello_msg(self, olt_id, peer):
        self.pOlt_Connection = GrpcChannel(self, name=olt_id)
        self.olt_peer = peer
        self.proxy.on_hello_message(olt_id)

    def peer_exists(self, peer):
        return peer == self.olt_peer

    def handle_Tx_message(self, onu_id, payload, peer):
        self.proxy.on_olt_message(onu_id, payload)

    def get_connection(self, peer):
        if self.peer_exists(peer):
            return self.pOlt_Connection
        else:
            return None

    def handle_ListenRx(self, channel):
        pass

    def remove_connection(self, peer):
        if peer == self.olt_peer:
            self.pOlt_Connection = None
            self.olt_peer = None


class GrpcChannel(CommonGrpcChannel):
    """ gRPC channel based on service specification in WT-451 working text """

    def __init__(self, grpc_server: 'GrpcServer', name: str):
        """ Class constructor.
        Args:
            grpc_server: parent GrpcServer
            name : vOMCI endpoint name
        """
        super().__init__(grpc_server)
        self.name = name  # OLT name

    def _disconnect_action(self):
        pass

    def _connect_action(self):
        pass

    def send(self, onu_id: 'OnuSbiId', msg: RawMessage) -> bool:
        """ Send message to ONU
        Args:
            onu_id: OnuSbiId" Tuple[str, int](PonID, TClayerONUid)
            msg: raw OMCI message without MIC
        Returns:
            True if successful
        """
        super().put_msg_in_queue(onu_id, msg)
        return True
