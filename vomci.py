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
from omcc.grpc.omci_channel_grpc import GrpcChannel
import omcc.grpc.omci_channel_grpc_server as grpc_server
from omh_nbi.omh_handler import OMHStatus
from omh_nbi.handlers.onu_activate import OnuActivateHandler
from database.omci_olt import *
from database.omci_olt import OltDatabase
import os

DEFAULT_BOOTSTRAP_SERVERS = kafka_interface.DEFAULT_BOOTSTRAP_SERVERS

logger = OmciLogger.getLogger(__name__)

VOMCI_GRPC_SERVER = True
# LOCAL_GRPC_SERVER_PORT = 58433
LOCAL_GRPC_SERVER_PORT = os.getenv("LOCAL_GRPC_SERVER_PORT", default=8433)


class VOmci:
    def __init__(self):
        self._name = "vomci1"
        self._kafka_if = None
        self._key_map = {}
        self._server = None

    def create_polt_connection(self) -> 'Olt':
        # Create gRPC channel and try to connect
        polt_host = '10.66.1.2'
        polt_port = 8433
        logger.info("connecting to {}:{}..".format(polt_host, polt_port))
        channel = GrpcChannel(name=self._name)
        olt = channel.connect(host=polt_host, port=polt_port)
        if olt is None:
            logger.warning("Test {}: connection failed".format(self._name))
            return None
        logger.info("Test {}: connected".format(self._name))
        return olt

    def trigger_kafka_response(self, handler):
        # TODO need to correlate request & response here.
        # possibly save the original; request in the handler
        logger.info("Sending kafka response for ONU {}, request/event {}: {}".format(
            handler.onu.onu_name, handler.user_data, handler.status))
        if handler.status == OMHStatus.OK:
            self._kafka_if.send_successful_response(handler.onu.onu_name)
        else:
            # TODO: Send NAK here
            logger.error("Request failed for ONU {}. Request/Event: {}".format(
                handler.onu.onu_name, handler.user_data))

    def trigger_onu_activate(self, olt_id: str, onu_name: str, channel_termination: str, onu_tc_id: int):
        onu_sbi_id = (channel_termination, onu_tc_id)
        # Add ONU to the database
        start_tci = 1
        # Check if ONU already exists. Create if not.
        olt = OltDatabase.OltGet(olt_id)
        if olt is None:
            logger.error("OLT with {} has not been connected yet".format(onu_name))
            return
        onu = olt.OnuGetByName(onu_name, False)
        if onu is None:
            onu = olt.OnuAdd(onu_name, onu_sbi_id, tci=start_tci)
            if onu is None:
                logger.error("Failed to create ONU {}".format(onu_name))
                # TODO: Send kafka NAK here
                return
            logger.info("ONU {} added to the database. Activating..".format(onu_name))
        else:
            logger.info("ONU {} exists. Re-activating..".format(onu_name))
        activate_handler = OnuActivateHandler(onu)
        # TODO: can store entire request here, including its correlation tag
        activate_handler.set_user_data('detect')
        activate_handler.start(self.trigger_kafka_response)

    def trigger_onu_undetect(self, olt_id: str, onu_name: str):
        olt = OltDatabase.OltGet(olt_id)
        if olt is None:
            logger.warning("OLT with {} has not been connected yet".format(onu_name))
            return
        if olt.OnuGetByName(onu_name, False) is not None:
            olt.OnuDelete(onu_name)
            logger.info("ONU {} deleted from the database".format(onu_name))
        self._kafka_if.send_successful_response(onu_name)

    def start(self):
        if not VOMCI_GRPC_SERVER:
            olt = self.create_polt_connection()
            if olt is None:
                return
        self._kafka_if = kafka_interface.KafkaInterface(self)
        self._kafka_if.start()

    def start_grpc_server(self):
        self._server = grpc_server.GrpcServer(port=LOCAL_GRPC_SERVER_PORT)
        self._server.create_listen_endpoint()
