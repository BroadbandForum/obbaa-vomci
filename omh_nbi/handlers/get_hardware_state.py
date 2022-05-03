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
# Get hardware state handler
#
# Created by Jafar Hamin (Nokia) on 25/03/2022
#

""" Get hardware state.

This handler is triggered when receiving ietf-hardware:hardware-state YANG object.
"""
from database.omci_me_types import *
from encode_decode.omci_action_set import SetAction
from encode_decode.omci_action_get import GetAction
from omh_nbi.omh_handler import OmhHandler, OMHStatus
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class GetHardwareStateHandler(OmhHandler):
    """ Get hardware state """

    def __init__(self, onu: 'OnuDriver'):
        """ Get hardware state

        Args:
            onu: ONU driver

        Returns:
            handler completion status
        """
        super().__init__(name='get_hardware_state', onu=onu,
                         description=' Get hardware state of onu {}'.format(onu.onu_id))

    def run_to_completion(self) -> OMHStatus:
        logger.info(self.info())
        sw_image_attrs = (1, 2, 3, 4)
        sw_image_me0 = sw_image_me(0)
        status =  self.transaction(GetAction(self, sw_image_me0, sw_image_attrs))
        if status != OMHStatus.OK:
            return status
        sw_image_me1 = sw_image_me(1)
        status = self.transaction(GetAction(self, sw_image_me1, sw_image_attrs))
        if status != OMHStatus.OK:
            return status
        onu_g_me0 = onu_g_me(0)
        onu_g_me_attrs = (1, 2)
        status = self.transaction(GetAction(self, onu_g_me0, onu_g_me_attrs))
        onu_g_me_attrs = (3,)
        status = self.transaction(GetAction(self, onu_g_me0, onu_g_me_attrs))
        if status != OMHStatus.OK:
            return status
        onu2_g_me_attrs = (1,)
        onu2_g_me0 = onu2_g_me(0)
        return self.transaction(GetAction(self, onu2_g_me0, onu2_g_me_attrs))
