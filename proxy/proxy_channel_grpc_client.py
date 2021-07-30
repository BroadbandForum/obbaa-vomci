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
from proxy.proxy import ProxyChannelDirection
import omcc.grpc.service_definition.tr451_vomci_sbi_message_pb2 as tr451_vomci_sbi_message_pb2
from omcc.grpc.grpc_client import GrpcClientChannel

logger = OmciLogger.getLogger(__name__)


class ProxyGrpcChannel(GrpcClientChannel):
    """ gRPC channel based on service specification in WT-451 working text """
    def __init__(self, proxy, name: str, direction, description: str = ''):
        """ Class constructor.
        Args:
            proxy: parent Proxy
            name : vOMCI endpoint name
            description: optional description
        """
        self._direction = direction
        self._parent = proxy
        super().__init__(name=name, description=description)

    @property
    def direction(self) -> ProxyChannelDirection:
        return self._direction

    def recv(self, vomci_msg : tr451_vomci_sbi_message_pb2):
        """ Message received via the channel.
            Hand it over to the proxy for forwarding
        """
        logger.info("ProxyGrpcClient: Received message")
        self._parent.recv(self, vomci_msg)
