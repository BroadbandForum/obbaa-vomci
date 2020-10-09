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
from omcc.omci_channel import OltCommChannel
from omh_nbi.onu_driver import OnuDriver
from omcc.grpc.grpc_server_common import CommonGrpcServer, CommonGrpcChannel

logger = OmciLogger.getLogger(__name__)


class GrpcServer(CommonGrpcServer):
    def __init__(self, port):
        super().__init__(port)
        self.pOlt_Connections = {}  # this is a dict that includes all the GrpcChannels

    def handle_hello_msg(self, olt_id, peer):
        channel = GrpcChannel(self, name=olt_id)
        self.pOlt_Connections[peer] = channel

    def peer_exists(self, peer):
        if peer in self.pOlt_Connections:
            return True
        else:
            logger.error("{} is not in pOLT_Connections".format(peer))
            return False

    def handle_Tx_message(self, onu_id, payload, peer):
        channel = self.get_connection(peer)
        if channel:
            channel._olt.recv(onu_id, payload)

    def get_connection(self, peer):
        if peer in self.pOlt_Connections:
            return self.pOlt_Connections[peer]
        else:
            return None

    def handle_ListenRx(self, channel):
        olt = channel.connected(channel._name)

    def remove_connection(self, peer):
        if peer in self.pOlt_Connections:
            del self.pOlt_Connections[peer]


class GrpcChannel(OltCommChannel, CommonGrpcChannel):
    """ gRPC channel based on service specification in WT-451 working text """

    def __init__(self, grpc_server: GrpcServer, name: str, description: str = ''):
        """ Class constructor.
        Args:
            name : vOMCI endpoint name
            description: optional description
        """
        OltCommChannel.__init__(self, name, description)
        CommonGrpcChannel.__init__(self, grpc_server)

    def _disconnect_action(self):
        logger.info("disconnected")
        self.disconnected()

    def _connect_action(self):
        logger.info("connected with {}".format(self._name))
        self.connected(self._name)

    def send(self, onu: 'OnuDriver', msg: RawMessage) -> bool:
        """ Send message to ONU
        Args:
            onu: ONU object
            msg: raw OMCI message without MIC
        Returns:
            True if successful
        """
        onu_id = onu.onu_id
        super().put_msg_in_queue(onu_id, msg)
        return True
