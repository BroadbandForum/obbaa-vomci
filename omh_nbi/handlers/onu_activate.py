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

#
# ONU activation handler
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" Activate ONU.

 This handler is triggered by ONU discovery event
 """
from database.omci_me_types import *
from database.omci_me import ME
from encode_decode.omci_action_get import GetAction
from encode_decode.omci_action_set import SetAction
from encode_decode.omci_action_create import CreateAction
from omh_nbi.onu_driver import OnuDriver
from omh_nbi.omh_handler import OmhHandler, OMHStatus
from omh_nbi.handlers.onu_mib_reset import OnuMibResetHandler
from omh_nbi.handlers.onu_mib_upload import OnuMibUploadHandler
from omci_logger import OmciLogger
from .omh_handler_utils import create_mac_bridge_port, create_ext_vlan_tag_oper_config_data
import copy

logger = OmciLogger.getLogger(__name__)

class OnuActivateHandler(OmhHandler):
    def __init__(self, onu: 'OnuDriver', force_reset: bool = False):
        """ ONU activation sequence.

            if not force_reset:
                GET onu_data.mib_sync
                if stored_onu_data.mib_sync == onu_data.mib_sync:
                    return OK
            Activate a new ONU:
                - MIB_RESET
                - MIB_UPLOAD
                - Create default GAL Ethernet Profile
        Args:
            onu:    OnuDriver instance, that includes stored ONU MIB
            force_reset: Force MIB reset if True
        Returns:
            handler completion status
        """
        super().__init__(name='activate_onu', onu = onu, description='activate_onu: {}'.format(onu.onu_id))
        self._force_reset = force_reset

    def _enable_uni(self, uni: ME) -> OMHStatus:
        """Enable UNI"""
        if uni.admin_state == 'UNLOCK':
            return OMHStatus.OK
        uni = copy.deepcopy(uni)
        uni.admin_state = 'UNLOCK'
        return self.transaction(SetAction(uni, ('admin_state',)))

    def run_to_completion(self) -> OMHStatus:
        # Check if ONU is already in sync
        logger.info('Starting activation of ONU {}'.format(self.onu.onu_id))
        onu_data = self.onu.get(omci_me_class['ONU_DATA'], 0, False)
        if not self._force_reset and onu_data is not None:
            action = GetAction(self, onu_data_me(0), ('mib_data_sync',))
            status = self.transaction(action)
            if status != OMHStatus.OK:
                return status
            if action.me.mib_data_sync == onu_data.mib_data_sync:
                logger.info('ONU {} is already in sync'.format(self.onu.onu_id))
                return OMHStatus.OK

        # Execute activation sequence
        if self.run_subsidiary(OnuMibResetHandler(self._onu)) != OMHStatus.OK:
            return self.status

        if self.run_subsidiary(OnuMibUploadHandler(self._onu)) != OMHStatus.OK:
            return self.status

        #
        # At this point ONU MIB is freshly populated. Start the initial provisioning
        #
        # 1. Create GAL Ethernet Profile if doesn't exist
        gal_eth_prof = self._onu.get_first(omci_me_class['GAL_ETH_PROF'])
        if gal_eth_prof is None:
            logger.info('{} ONU {}: Create GAL EThernet Profile'.format(self._name, self.onu.onu_id))
            gal_eth_prof = gal_eth_prof_me(1)
            gal_eth_prof.max_gem_payload_size = 4095 # Default value
            action = CreateAction(self, gal_eth_prof)
            status = self.transaction(action)
            if status != OMHStatus.OK:
                return status
        gal_eth_prof.user_name = 'gal_eth_prof'
        self._onu.set(gal_eth_prof)

        # 2. Create MAC bridge service profile if doesn't exist
        mac_bridge_svc_prof = self._onu.get_first(omci_me_class['MAC_BRIDGE_SVC_PROF'])
        if mac_bridge_svc_prof is None:
            logger.info('{} - Create MAC Bridge Service Profile'.format(self.info()))
            mac_bridge_svc_prof = mac_bridge_svc_prof_me(1)
            mac_bridge_svc_prof.dynamic_filtering_ageing_time = 300 # Default value
            action = CreateAction(self, mac_bridge_svc_prof)
            status = self.transaction(action)
            if status != OMHStatus.OK:
                return status

        return OMHStatus.OK
