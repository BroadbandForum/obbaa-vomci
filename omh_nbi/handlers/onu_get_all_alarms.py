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
# 
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" 

Usually this handler is executed as a part of ONU activation when a new ONU is discovered
"""
from omh_nbi.onu_driver import OnuDriver
from omh_nbi.omh_handler import OmhHandler, OMHStatus
from encode_decode.omci_action_get_all_alarms import GetAllAlarmsAction
from encode_decode.omci_action_get_all_alarms_next import GetAllAlarmsNextAction
from omci_logger import OmciLogger
from omh_nbi.handlers.alarm_handler import AlarmHandler

logger = OmciLogger.getLogger(__name__)

class GetAllAlarmsHandler(OmhHandler):
    def __init__(self, onu: 'OnuDriver'):
        super().__init__(name='get_all_alarms', onu = onu, description='get_all_alarms: {}'.format(onu.onu_id))
        self._num_me_decoded = 0

    def run_to_completion(self) -> OMHStatus:
        

        get_all_alarms_action = GetAllAlarmsAction(self)
        status = self.transaction(get_all_alarms_action)
        if status != OMHStatus.OK:
            return status
        AlarmHandler.seq_number = 0
        get_all_alarms_next_action = GetAllAlarmsNextAction(self)
        for cmd in range(get_all_alarms_action.num_of_get_all_alarms_next):
            get_all_alarms_next_action.reinit()
            status = self.transaction(cmd == 0 and get_all_alarms_next_action or None)
            if status != OMHStatus.OK:
                break
            me = get_all_alarms_next_action.search_ent_cls
            if me is not None:
                # Merge with existing ME if exists or add to the MIB if not
                old_me = self.onu.get(me.me_class, me.inst, False)
                if old_me is not None:
                    old_me.merge(me)
                else:
                    self._onu.add(me)
                    self._num_me_decoded += 1
        if status == OMHStatus.OK:
            AlarmHandler.notify_received_get_all_alarms()
        return status

    def stats(self) -> str:
        return super().stats() + ' MEs:{}'.format(self._num_me_decoded)
