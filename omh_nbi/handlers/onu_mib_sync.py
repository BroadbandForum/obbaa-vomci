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

"""
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

class OnuMibDataSyncHandler(OmhHandler):
    def __init__(self, onu: 'OnuDriver'):
        """
            GET onu_data.mib_sync
            if stored_onu_data.mib_sync == onu_data.mib_sync:
                return OK
        Args:
            onu:    OnuDriver instance, that includes stored ONU MIB
        Returns:
            handler completion status
        """
        super().__init__(name='mib_sync_onu', onu = onu, description='mib_sync_onu: {}'.format(onu.onu_id))
        self.is_aligned = False
        self.datastore_tag = ""

    def run_to_completion(self) -> OMHStatus:
        # Check if ONU is already in sync
        logger.info('Starting MIB sync for ONU {}'.format(self.onu.onu_id))
        onu_data = self.onu.get(omci_me_class['ONU_DATA'], 0, False)
        if onu_data is not None:
            action = GetAction(self, onu_data_me(0), ('mib_data_sync',))
            status = self.transaction(action)
            if status != OMHStatus.OK:
                return status
            if action.me.mib_data_sync == onu_data.mib_data_sync and onu_data.mib_data_sync != 0:
                logger.info('ONU {} is in sync. mib_data_sync={}'.format(self.onu.onu_id, onu_data.mib_data_sync))
                self.is_aligned = True      
                return OMHStatus.OK
            logger.info('ONU {} is not in sync. Expected mib_data_sync {} got {}'.format(
                self.onu.onu_id, onu_data.mib_data_sync, action.me.mib_data_sync))
        return OMHStatus.OK
