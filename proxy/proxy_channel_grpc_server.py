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

import omcc.grpc.service_definition.tr451_vomci_sbi_message_pb2 as tr451_vomci_sbi_message_pb2
from omci_types import *
from omci_logger import OmciLogger
from omcc.grpc.grpc_server import GrpcServer, GrpcServerChannel
from proxy.proxy import ProxyChannelDirection
logger = OmciLogger.getLogger(__name__)


class GrpcProxyServerChannel(GrpcServerChannel):
    """ gRPC proxy server channel """
    def __init__(self, server: 'GrpcProxyServer', name: str, description: str, direction=None, remote_endpoint: str = None):
        """ Class constructor.
        Args:
            server: parent GrpcProxyServer
            name : vOMCI endpoint name
        """
        if direction is None:
            self._direction = ProxyChannelDirection.Downstream
        else:
            self._direction = direction
        self.server = server
        super().__init__(name=name, server=server, description=description, remote_endpoint=remote_endpoint)

    @property
    def direction(self) -> ProxyChannelDirection:
        return self._direction

    def get_olt_name(self):
        """
            Return name of managed olt. In the case of
            the proxy's grpc server, there will only be
            one managed olt per grpc server __channel__,
            (but multiple olts per grpc __server__)
            so return from the first value of the dict.
        """
        all_olts = list(self._olts.values())
        if len(all_olts) == 0:
            return None
        (olt_name, endpoint_name) = all_olts[0].id
        return olt_name

    def recv(self, vomci_msg : tr451_vomci_sbi_message_pb2):
        """ Message received via the channel.
            Hand it over to the proxy for forwarding
        """
        logger.info("GrpcProxyServerChannel: Received message")
        self.server._parent.recv(self, vomci_msg)


class GrpcProxyServer(GrpcServer):
    """ Proxy gRPC server """
    def __init__(self, parent, name, port):
        super().__init__(name=name, port=port, connection_type=GrpcProxyServerChannel, parent=parent)
