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
# MIB upload handler
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" Upload ONU MIB,

Usually this handler is executed as a part of ONU activation when a new ONU is discovered
"""
from omh_nbi.onu_driver import OnuDriver
from omh_nbi.omh_handler import OmhHandler, OMHStatus
from encode_decode.omci_action_mib_upload import MibUploadAction
from encode_decode.omci_action_mib_upload_next import MibUploadNextAction
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class OnuMibUploadHandler(OmhHandler):
    def __init__(self, onu: 'OnuDriver'):
        super().__init__(name='mib_upload', onu = onu, description='mib_upload: {}'.format(onu.onu_id))
        self._num_me_decoded = 0

    def run_to_completion(self) -> OMHStatus:
        # ONU MIB Upload sequence:
        # - MIB_UPLOAD(onu_data.0) --> number of the following MIB_UPLOAD_NEXT commands
        # - for i in range(number_of_mib_upload_next_commands):
        #      MIB_UPLOAD_NEXT(i)
        self.onu.clear()
        upload_action = MibUploadAction(self)
        status = self.transaction(upload_action)
        if status != OMHStatus.OK:
            return status
        upload_next_action = MibUploadNextAction(self)
        for cmd in range(upload_action.num_of_upload_next):
            upload_next_action.reinit()
            status = self.transaction(cmd == 0 and upload_next_action or None)
            if status != OMHStatus.OK:
                break
            me = upload_next_action.upload_me
            if me is not None:
                # Merge with existing ME if exists or add to the MIB if not
                old_me = self.onu.get(me.me_class, me.inst, False)
                if old_me is not None:
                    old_me.merge(me)
                else:
                    self._onu.add(me)
                    self._num_me_decoded += 1
        return status

    def stats(self) -> str:
        return super().stats() + ' MEs:{}'.format(self._num_me_decoded)
