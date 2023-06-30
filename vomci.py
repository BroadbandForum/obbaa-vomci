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
# from nbi import kafka_interface
from typing import Tuple
from nbi import kafka_proto_interface as kafka_interface
from omcc.grpc.grpc_client import GrpcClientChannel
from omcc.grpc.grpc_server import GrpcServer, GrpcServerChannel
from omh_nbi.omh_handler import OMHStatus
from omh_nbi.handlers.onu_activate import OnuActivateHandler
from omh_nbi.handlers.onu_mib_sync import OnuMibDataSyncHandler
from database.omci_olt import *
from database.omci_olt import OltDatabase
from database.onu_management_chain import ManagementChain
from database.telemetry_subscription import Subscription
from mapper.yang_to_omci_mapper import YangtoOmciMapperHandler, get_xpath_handler

from vnf import VNF
import os, time, threading

DEFAULT_BOOTSTRAP_SERVERS = kafka_interface.DEFAULT_BOOTSTRAP_SERVERS

logger = OmciLogger.getLogger(__name__)

VOMCI_NAME = os.getenv('VOMCI_KAFKA_SENDER_NAME', 'obbaa-vomci')

class VOmci(VNF):
    def __init__(self, db_location, name=None):
        if name is None:
            name = VOMCI_NAME
        super().__init__(db_location, name)

    @property
    def name(self):
        return self._name

    def start(self):
        Subscription.set_push_call_back(self.trigger_push_subscribed_xpaths)
        super().start()

    def create_polt_connection(self):
        # Create gRPC channel and try to connect
        polt_host = '10.66.1.2'
        polt_port = 8433
        logger.info("connecting to {}:{}..".format(polt_host, polt_port))
        channel = GrpcClientChannel(name=self._name)
        ret_val = channel.connect(host=polt_host, port=polt_port)
        if not ret_val:
            logger.warning("Test {}: connection failed".format(self._name))
            return False
        logger.info("Test {}: connected".format(self._name))
        return True

    def add_managed_onus(self, comm_channel):
        """
        Add managed onus to communication channel, as per configuration.
        This function should be called by the GrpcServer when
        a new client connection is initiated.
        """
        for managed_onu in ManagementChain.GetManagedOnus():
            if managed_onu.downstream_endpoint_name == comm_channel.remote_endpoint_name:
                onu_id = (managed_onu.ct_ref, managed_onu.onu_id)
                comm_channel.add_managed_onu(managed_onu.olt_name, managed_onu.onu_name, onu_id)

    def trigger_start_grpc_server(self, name, remote_adress, remote_port = 8443):
        if self._server is not None:
            self._server.stop()
        self._server = GrpcServer(remote_adress, remote_port, name, parent=self)

    def trigger_create_onu(self, onu_name) -> (bool, str):
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
        logger.info("Onu {} was created in vOMCi".format(onu_name))
        self._kafka_if.send_successful_response(onu_name)

    def trigger_set_onu_communication(self, olt_name: str, onu_name: str, channel_termination: str,
                                      onu_tc_id: int, available: bool, olt_endpoint_name: str,
                                      voltmf_endpoint_name: str, voltmf_name: str):
        """
        Use arguments to set/update the communication points and management chain
        of given ONU. Then initiate the ONU detect sequence. To be called by
        the kafka interface when a "set ONU communication" request is received.
        """

        if self._server is None:
            logger.error("No grpc connection established!")
            return

        managed_onu = ManagementChain.SetOnuCommunication(olt_name, onu_name, channel_termination,
                                                          onu_tc_id, available, olt_endpoint_name,
                                                          voltmf_endpoint_name, voltmf_name)
        # Assign channel if communication is available
        channel = None
        for channel in self._server.connections().values():
            if managed_onu.downstream_endpoint_name == channel.remote_endpoint_name:
                onu_id = (managed_onu.ct_ref, managed_onu.onu_id)
                channel.add_managed_onu(managed_onu.olt_name, onu_name, onu_id)
                break
        managed_onu.SetDsChannel(channel)
        if available:
            if channel is None:
                error_msg = "ONU {}: can't enable communication. remote-endpoint {} is not connected".format(
                    onu_name, managed_onu.downstream_endpoint_name)
                logger.error(error_msg)
                self._kafka_if.send_unsuccessful_response(onu_name, error_msg=error_msg)
            self.trigger_onu_mib_sync(olt_name, olt_endpoint_name, onu_name, channel_termination, onu_tc_id)
        else:
            self._kafka_if.send_successful_response(onu_name)

    def trigger_kafka_response(self, handler):
        # TODO need to correlate request & response here.
        # possibly save the original; request in the handler
        if handler._subscription_id is not None:
            logger.debug("Sending telemetry notification for subscription ID {} ONU {} Xpaths".format(
                handler._subscription_id, handler.onu, str(handler.xpaths)))
            self._kafka_if.send_telemetry_notification(handler.onu, handler.xpaths, handler.subscription_id)
            return
        logger.debug("Sending kafka response for ONU {}, request/event {}: {}".format(
            handler.onu.onu_name, handler.user_data, handler.status))
        if handler.status == OMHStatus.OK:
            self._kafka_if.send_successful_response(handler.onu)
        else:
            self._kafka_if.send_unsuccessful_response(handler.onu.onu_name, error_msg=str(handler.status))
            logger.error("Request failed for ONU {}. Request/Event: {}. Error {}".format(
                handler.onu.onu_name, handler.user_data, handler.status))

    def trigger_kafka_align_notification(self, handler):
        logger.debug("Sending kafka alignment notification for ONU {}, request/event {}: status={} aligned={}".format(
            handler.onu.onu_name, handler.user_data, handler.status, handler.is_aligned))
        self._kafka_if.send_alignment_notification(handler.onu.onu_name, handler.is_aligned)

    def trigger_onu_mib_sync(self, olt_id: str, remote_endpoint_name: str, onu_name: str, channel_termination: str,
                             onu_tc_id: int):
        onu_sbi_id = (channel_termination, onu_tc_id)
        # Add ONU to the database
        start_tci = 1
        # Check if ONU already exists. Create if not.
        logger.info('ONU MIB sync: ONU {}.{} at OLT {}. remote_endpoint_name:{}'.format(
            channel_termination, onu_tc_id, olt_id, remote_endpoint_name))

        olt = OltDatabase.OltGet((olt_id, remote_endpoint_name))
        if olt is None:
            logger.error("OLT {} with {} has not been connected yet".format(olt_id, onu_name))
            self._kafka_if.send_unsuccessful_response(onu_name)
            return

        onu = olt.OnuGetByName(onu_name, False)
        if onu is None:
            logger.error("ONU {} doesn't exist. It must be created first using create-onu RPC".format(onu_name))
            self._kafka_if.send_unsuccessful_response(onu_name)
            return

        self._kafka_if.send_successful_response(onu_name)
        mib_sync_handler = OnuMibDataSyncHandler(onu)
        # TODO: can store entire request here, including its correlation tag
        mib_sync_handler.set_user_data('detect')
        mib_sync_handler.start(self.trigger_kafka_align_notification)

    def trigger_delete_onu(self, onu_name: str):
        managed_onu = ManagementChain.DeleteOnu(onu_name)
        if managed_onu is None:
            logger.warning("Cannot delete ONU {} that has not been created".format(onu_name))
            self._kafka_if.send_unsuccessful_response(onu_name)
            return
        logger.info("ONU {} deleted from the managed-onus database".format(onu_name))
        polt_id = (managed_onu.olt_name, managed_onu.downstream_endpoint_name)
        olt = OltDatabase.OltGet(polt_id)
        if olt is not None:
            if olt.OnuGetByName(onu_name, False) is not None:
                olt.OnuDelete(onu_name)
                logger.info("ONU {} MIB deleted from the database".format(onu_name))
        self._kafka_if.send_successful_response(onu_name)

    def trigger_push_subscribed_xpaths(self, onu_name, subscription_id, xpaths):
        logger.info("Collecting telemetry data for subscription {} ONU {} XPaths {}".format(subscription_id, onu_name, xpaths))
        onu = VOmci.__get_onu_by_name(onu_name)
        if onu is None:
            logger.warn("ONU {} does not exist for collecting telemetry data".format(onu_name))
            return
        mapperObj = YangtoOmciMapperHandler(self, onu)
        mapperObj.set_subscription_xpaths(subscription_id, xpaths)
        for xpath in xpaths:
            mapperObj.add_handler(get_xpath_handler(xpath), None)
        mapperObj.run()

    @staticmethod
    def __get_onu_by_name(onu_name):
        managed_onu = ManagementChain.GetOnu(onu_name)
        if managed_onu is None:
            return None
        olt_name = (managed_onu.olt_name, managed_onu.downstream_endpoint_name)
        olt = OltDatabase().OltGet(olt_name)
        if olt is None:
            return None
        return olt.OnuGetByName(onu_name, False)