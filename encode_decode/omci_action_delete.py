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
# omci_action_delete.py : "DELETE" OMCI action encoder/decoder
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

"""DELETE action"""
from omci_types import *
from database.omci_me import ME
from database.omci_me_types import omci_msg_type
from encode_decode.omci_action import OmciAction
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class DeleteAction(OmciAction):
    """ SetRequest: DELETE Request control block.

    When OMCI request-response transaction is completed, the message block
    contains the following attributes:
        me
        omci_result: 0=good, otherwise bad (see omci_result_code Enum)
    """
    name = 'DELETE'
    action = omci_msg_type[name]

    def __init__(self, owner: 'OmhHandler', me: ME, extended : bool = False):
        """
        Args:
            owner: request owner
            me: ME to be sent
            extended: pass True to generate an extended OMCI message
        """
        assert self.name.lower() in me.actions
        super().__init__(self.action, me, True, False, extended, owner)

    def encode_content(self) -> RawMessage:
        """Encode CREATE request message content.

        Returns:
            raw OMCI message content
        """
        return bytearray()

    def decode_content(self, msg: RawMessage) -> bool:
        """Decode CREATE response message content.

        Returns:
            result : True if successful
        """
        if self._ak:
            # MIB_RESET response - normal flow
            self._omci_result = struct.unpack_from("!H", msg, self.content_offset)[0]
        return True

    def commit(self, onu: 'OnuDriver'):
        """ Commit action results top ONU MIB/

        Args:
            onu : OnuDriver containing the current ONU MIB
        Raises: an exception in case of commit failure
        """
        if not onu.delete(self._me.me_class, self._me.inst):
            raise Exception('{} - failed to commit to the local MIB'.format(self.name))

    @property
    def is_configuration(self):
        """ Return TRUE for configuration handlers that affect mib_sync """
        return True
