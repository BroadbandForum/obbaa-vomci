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
# MIB reset handler
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" Reset ONU MIB.

Usually this handler is executed as a part of ONU activation when a new ONU is discovered
"""
from omh_nbi.onu_driver import OnuDriver
from omh_nbi.omh_handler import OmhHandler, OMHStatus
from encode_decode.omci_action_mib_reset import MibResetAction
from encode_decode import omci_action_mib_reset
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class OnuMibResetHandler(OmhHandler):
    def __init__(self, onu: 'OnuDriver'):
        super().__init__(name='mib_reset', onu = onu, description='mib_reset: {}'.format(onu.onu_id))

    def run_to_completion(self) -> OMHStatus:
        self.onu.clear()
        return self.transaction(MibResetAction(self))
