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
# UNI handler. Provisions per-ONU-UNI MEs
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" Set up UNI port handler.

 This handler is triggered by creation of YANG object representing ONU UNI.
 It performs the following sequence:
    - Enable UNI
    - Create MAC Bridge Port Config Data
    - Create EXT_VLAN_TAG_OPER_CFG
    - Set EXT_VLAN_TAG_OPER_CFG
    - Create Multicast Operations Profile
    - Create Multicast Subscriber Config Info
"""
from database.omci_me_types import *
from database.omci_me import ME
from encode_decode.omci_action_set import SetAction
from encode_decode.omci_action_create import CreateAction
from omh_nbi.onu_driver import OnuDriver
from omh_nbi.omh_handler import OmhHandler, OMHStatus
from omci_logger import OmciLogger
from .omh_handler_utils import get_uni, create_mac_bridge_port, create_ext_vlan_tag_oper_config_data
import copy

logger = OmciLogger.getLogger(__name__)

class UniSetHandler(OmhHandler):
    def __init__(self, onu: 'OnuDriver', uni_name: str, uni_id: int):
        """ Set UNI port.

        Args:
            uni_name : UNI interface name in the YANG model
            uni_id: 0-based UNI index. Usually it is determined by parent-rel-pos attribute in the
                    parent hardware component. Note that unlike parent-rel-pos, uni_id is 0-based.
                    The corresponding ME of type PPTP_Eth_UNI=11, VEIP_InterfacePoint=329 must exist
                    in the ONU MIB.
        Returns:
            handler completion status
        """
        super().__init__(name='set_uni', onu = onu, description='set_uni: {}.{}-{}'.format(onu.onu_id, uni_id, uni_name))
        self._uni_name = uni_name
        self._uni_id = uni_id

    def _enable_uni(self, uni: ME) -> OMHStatus:
        """Enable UNI"""
        if uni.admin_state == 'UNLOCK':
            return OMHStatus.OK
        uni = copy.deepcopy(uni)
        uni.admin_state = 'UNLOCK'
        return self.transaction(SetAction(self, uni, ('admin_state',)))

    def run_to_completion(self) -> OMHStatus:
        logger.info(self.info())

        # Do nothing if UNI is already in the local MIB
        if self._onu.get_by_name(self._uni_name) is not None:
            logger.info('{} - Already configured'.format(self.info()))
            return OMHStatus.OK

        #
        # At this point ONU MIB is freshly populated. Start the initial provisioning
        #
        uni_me = get_uni(self._onu, self._uni_id)
        if uni_me is None:
            return self.logerr_and_return(OMHStatus.ERROR_IN_PARAMETERS,
                                          'UNI {} is not found'.format(self._uni_id))

        # 2. Enable UNI
        logger.info('{} - Enable'.format(self.info()))
        status = self._enable_uni(uni_me)
        if status != OMHStatus.OK:
            return status

        # 3. Create MAC Bridge Port Config Data ME
        logger.info('{} - Create MAC Bridge Port'.format(self.info()))
        status = create_mac_bridge_port(self, uni_me)
        if status != OMHStatus.OK:
            return status

        # 4. Create EXT_VLAN_TAG_OPER_CFG
        logger.info('{} - Create EXT VLAN Tagging Oper Config Data'.format(self.info()))
        status = create_ext_vlan_tag_oper_config_data(self, uni_me)
        if status != OMHStatus.OK:
            return status

        uni_me.user_name = self._uni_name
        self._onu.set(uni_me)

        # XXX TODO
        # - Create Multicast Operations Profile
        # - Create Multicast Subscriber Config Info

        return OMHStatus.OK
