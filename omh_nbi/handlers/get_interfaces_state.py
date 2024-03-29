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
# Get interfaces state handler
#
# Created by Jafar Hamin (Nokia) on 25/03/2022
#

""" Get interfaces state.

This handler is triggered when receiving ietf-interfaces:interfaces-state YANG object.
"""
from database.omci_me_types import *
from encode_decode.omci_action_set import SetAction
from encode_decode.omci_action_get import GetAction
from omh_nbi.omh_handler import OmhHandler, OMHStatus
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class GetInterfacesStateHandler(OmhHandler):
    """ Get interfaces state """

    def __init__(self, onu: 'OnuDriver'):
        """ Get interfaces state

        Args:
            onu: ONU driver

        Returns:
            handler completion status
        """
        super().__init__(name='get_interfaces_state', onu=onu,
                         description=' Get interfaces state of onu {}'.format(onu.onu_id))

    def run_to_completion(self) -> OMHStatus:
        logger.info(self.info())
        unis = self._onu.get_all_instances(omci_me_class['PPTP_ETH_UNI'])
        uni_me_attrs = (5, 6)
        for uni in unis:
            uni_me = pptp_eth_uni_me(uni.me_inst)
            status =  self.transaction(GetAction(self, uni_me, uni_me_attrs))
            if status != OMHStatus.OK:
                return status

        mbpcds = self._onu.get_all_instances(omci_me_class['MAC_BRIDGE_PORT_CONFIG_DATA'])
        mbpcd_me_attrs = (3, 4)
        for mbpcd in mbpcds:
            mbpcd_me = mac_bridge_port_config_data_me(mbpcd.me_inst)
            status =  self.transaction(GetAction(self, mbpcd_me, mbpcd_me_attrs))
            if status != OMHStatus.OK:
                return status

        pm_ups = self._onu.get_all_instances(omci_me_class['ETH_FRAME_UPSTREAM_PM'])
        pm_up_me_attrs = (4, 6, 7)
        for pm_up in pm_ups:
            pm_up_me = eth_frame_upstream_pm_me(pm_up.me_inst)
            status =  self.transaction(GetAction(self, pm_up_me, pm_up_me_attrs))
            if status != OMHStatus.OK:
                return status

        pm_downs = self._onu.get_all_instances(omci_me_class['ETH_FRAME_DOWNSTREAM_PM'])
        pm_down_me_attrs = (4, 6, 7)
        for pm_down in pm_downs:
            pm_down_me = eth_frame_downstream_pm_me(pm_down.me_inst)
            status =  self.transaction(GetAction(self, pm_down_me, pm_down_me_attrs))
            if status != OMHStatus.OK:
                return status
    
        anis = self._onu.get_all_instances(omci_me_class['ANI_G'])
        ani_me_attrs = (1,)
        for ani in anis:
            ani_me = ani_g_me(ani.me_inst)
            status =  self.transaction(GetAction(self, ani_me, ani_me_attrs))
            if status != OMHStatus.OK:
                return status
        return OMHStatus.OK
