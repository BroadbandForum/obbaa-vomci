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
# OMH handler that creates a GEM port.
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" Create a GEM port,

This handler is triggered by creation /bbf-xpongemtcont:xpongemtcont or
/bbf-xpon:xpon/multicast-gemports YANG object.

TODO: need more work for multicast
TODO: need more work for non TR-156 case, when a single GEM port goes to multiple UNIs
"""
from database.omci_me_types import *
from encode_decode.omci_action_set import SetAction
from encode_decode.omci_action_create import CreateAction
from .omh_handler_utils import get_uni, get_queue_by_owner_tc
from omh_nbi.omh_handler import OmhHandler, OMHStatus
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class GemPortCreateHandler(OmhHandler):
    """ Create a GEM Port """

    def __init__(self, onu: 'OnuDriver', gem_port_name: str,
                 uni_name: str, tcont_name: Optional[str],
                 gem_port_id: int, tc: int, direction='BIDIRECTIONAL',
                 encryption='NO_ENCRYPTION'):
        """ Create a GEM Port Network CTP ME

        Args:
            onu: ONU driver
            gem_port_name: GEM port object name
            uni: UNI port name or index
            tcont_name: TCONT object name
            gem_port_id: GEM port id
            tc: Traffic class
            direction: one of the values of gem_port_net_ctp_direction enum
            encryption: one of the values of gem_port_net_ctp_encryption_key_ring enum
        Returns:
            handler completion status
        """
        super().__init__(name='gem_port_create', onu=onu,
                         description=' Create GEM Port Network CTP on {}'.format(onu.onu_id))
        self._gem_port_name = gem_port_name
        self._uni_name = uni_name
        self._tcont_name = tcont_name
        self._gem_port_id = gem_port_id
        self._tc = tc
        self._direction = direction
        self._encryption = encryption
        self._is_upstream = direction == 'BIDIRECTIONAL' or direction == 'UNI_TO_ANI'
        self._is_downstream = direction == 'BIDIRECTIONAL' or direction == 'ANI_TO_UNI'

    def run_to_completion(self) -> OMHStatus:
        logger.info(self.info())

        # Validate parameters and fetch the relevant MEs
        tcont_me = None
        if self._is_upstream:
            tcont_me = self._onu.get_by_name(self._tcont_name)
            if tcont_me is None:
                return self.logerr_and_return(OMHStatus.ERROR_IN_PARAMETERS,
                                              'TCONT {} is not found'.format(self._tcont_name))

        uni_me = get_uni(self._onu, self._uni_name)
        if uni_me is None:
            return self.logerr_and_return(OMHStatus.ERROR_IN_PARAMETERS,
                                          'UNI {} is not found'.format(self._uni_name))

        ds_queue_me = None
        if self._is_downstream:
            ds_queue_me = get_queue_by_owner_tc(self._onu, False, uni_me, self._tc)

        us_queue_me = None
        if self._is_upstream:
            us_queue_me = get_queue_by_owner_tc(self._onu, True, tcont_me, self._tc)

        me = gem_port_net_ctp_me(
            self._gem_port_id,
            port_id=self._gem_port_id,
            direction=self._direction,
            tcont_ptr=tcont_me is not None and tcont_me.inst or OMCI_NULL_PTR,
            traffic_desc_prof_ptr_us=OMCI_NULL_PTR, # XXX for now
            traffic_mgmt_ptr_us=us_queue_me is not None and us_queue_me.inst or OMCI_NULL_PTR,
            traffic_desc_prof_ptr_ds=OMCI_NULL_PTR, # XXX for now
            pri_queue_ptr_ds=ds_queue_me is not None and ds_queue_me.inst or OMCI_NULL_PTR,
            encryption_key_ring=self._encryption)
        me.user_name = self._gem_port_id
        me.set_user_attr('tc', self._tc)
        me.set_user_attr('uni', self._uni_name)

        return self.transaction(CreateAction(self, me))
