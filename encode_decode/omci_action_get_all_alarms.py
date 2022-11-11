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
# omci_action_get_all_alarms.py : "GET_ALL_ALARMS" OMCI action encoder/decoder
#

"""GET_ALL_ALARMS action"""
from omci_types import *
from database.omci_me import ME
from database.omci_me_types import omci_msg_type, onu_data_me
from encode_decode.omci_action import OmciAction
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class GetAllAlarmsAction(OmciAction):
    """ GetAllAlarmsAction: Get All Alarms control block
    When OMCI request-response transaction is completed, the message block.

    contains the following attributes:
       me
        num_of_upload_next: number of subsequent MIB upload next commands
    """
    name = 'GET_ALL_ALARMS'
    action = omci_msg_type[name]

    def __init__(self, owner: 'OmhHandler' = None):
        """
        Args:
            owner: request owner
        """
        me = onu_data_me(0)
        super().__init__(self.action, me, True, False, False, owner)

        self._num_of_get_all_alarms_next = 0
        self._alarm_retrieval_mode = 0 or 1

    def encode_content(self) -> RawMessage:
        """Encode GET_ALL_ALARMS request message content.

        Returns:
            raw OMCI message content
        """
        if not self._ak:
            # GET_ALL_ALARMS request 
            msg = struct.pack("!B", self._alarm_retrieval_mode)
        else:
            # GET_ALL_ALARMS response 
            msg = struct.pack("!H", self._num_of_get_all_alarms_next)
        return msg

    def decode_content(self, msg: RawMessage) -> bool:
        """Decode GET_ALL_ALARMS message content.

        Returns:
            message content
        """
        if self._ak:
            # GET_ALL_ALARMS response 
            self._num_of_get_all_alarms_next = struct.unpack_from("!H",msg,self.content_offset)[0]
        else:
            # GET_ALL_ALARMS request
            self._alarm_retrieval_mode = struct.unpack_from("!B", msg, self.content_offset)[0]

        return True 
