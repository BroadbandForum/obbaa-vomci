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
# omci_action_mib_reset.py : "MIB_RESET" OMCI action encoder/decoder
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

"""MIB_RESET action"""
from omci_types import *
from database.omci_me import ME
from database.omci_me_types import omci_msg_type, onu_data_me
from encode_decode.omci_action import OmciAction
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class MibResetAction(OmciAction):
    """ MibReset: MIB_RESET control block.

    When OMCI request-response transaction is completed, the message block
    contains the following attributes:
        me
        omci_result: 0=good, otherwise bad (see omci_result_code Enum)
    """
    name = 'MIB_RESET'
    action = omci_msg_type[name]

    def __init__(self, owner: 'OmhHandler'):
        """
        Args:
            owner: request owner
        """
        me = onu_data_me(0)
        super().__init__(self.action, me, True, False, False, owner)

    def encode_content(self) -> RawMessage:
        """Encode MIB_RESET message content.

        Returns:
            raw OMCI message content
        """
        if not self._ak:
            # MIB_RESET request - normal flow
            msg = bytearray()
        else:
            # MIB_RESET response - mainly for debugging
            msg = struct.pack("!H", self._omci_result)
        return msg

    def decode_content(self, msg: RawMessage) -> bool:
        """Decode MIB_RESET message content.

        Returns:
            result : True if successful
        """
        if self._ak:
            # MIB_RESET response - normal flow
            self._omci_result = struct.unpack_from("!H", msg, self.content_offset)[0]
        return True
