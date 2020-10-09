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
# TCONT creation handler
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" Create a TCONT.

This handler is triggered by creation /bbf-xpongemtcont:xpongemtcont YANG object.
"""
from database.omci_me_types import *
from encode_decode.omci_action_set import SetAction
from omh_nbi.omh_handler import OmhHandler, OMHStatus
from omci_logger import OmciLogger
import copy

logger = OmciLogger.getLogger(__name__)

class TcontCreateHandler(OmhHandler):
    """ Create a TCONT """

    def __init__(self, onu: 'OnuDriver', tcont_name: str,
                 alloc_id: int, policy: Optional[str] = None):
        """ Set a TCONT ME

        Args:
            onu: ONU driver
            tcont_name: GEM port object name
            alloc_id: Alloc Id
        Returns:
            handler completion status
        """
        super().__init__(name='tcont_create', onu=onu,
                         description=' Set TCONT on {}'.format(onu.onu_id))
        self._tcont_name = tcont_name
        self._alloc_id = alloc_id
        self._policy = policy

    def _get_free_tcont(self) -> ME:
        """ Get unused TCONT ME
            Returns:
                Unused TCONT ME or None if not found
        """
        all_tconts = self._onu.get_all_instances(omci_me_class['TCONT'])
        for tcont in all_tconts:
            if tcont.alloc_id == 0xffff or tcont.alloc_id == 0xff:
                return tcont
        return None

    def run_to_completion(self) -> OMHStatus:
        logger.info(self.info())

        # Validate parameters and fetch the relevant MEs
        tcont_me = self._get_free_tcont()
        if tcont_me is None:
            return self.logerr_and_return(OMHStatus.NO_RESOURCES,
                                          "Can't create {}. No free TCONTs".format(self._tcont_name))
        # Create a copy so that MIB remains unchanged until commit
        tcont_me = copy.deepcopy(tcont_me)
        tcont_me.alloc_id = self._alloc_id
        attrs = ('alloc_id',)
        if self._policy is not None:
            tcont_me.policy = self._policy
            attrs += ('policy',)
        tcont_me.user_name = self._tcont_name
        return self.transaction(SetAction(self, tcont_me, attrs))
