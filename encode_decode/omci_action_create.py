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
# omci_action_create.py : "CREATE" OMCI action encoder/decoder
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

"""CREATE action"""
from omci_types import *
from database.omci_me import ME
from database.omci_me_types import omci_msg_type
from encode_decode.omci_action import OmciAction
from encode_decode.omci_action_delete import DeleteAction
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class CreateAction(OmciAction):
    """ SetRequest: CREATE Request control block.

    When OMCI request-response transaction is completed, the message block
    contains the following attributes:
        me
        omci_result: 0=good, otherwise bad (see omci_result_code Enum)
        attr_exec_mask: Attribute execution mask: 1 for every failed attribute.
                     contains a valid value only if omci_result=9
    """
    name = 'CREATE'
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
        self.set_attr_mask(me.attr_mask(access='C'))
        self._attr_exec_mask = 0

    def encode_content(self) -> RawMessage:
        """Encode CREATE request message content.

        Returns:
            raw OMCI message content
        """
        if not self._ak:
            # CREATE request - normal flow
            msg = self.encode_attributes(bytearray())
        else:
            # CREATE response - mainly for debugging
            msg = struct.pack("!HH", self._omci_result, self._attr_exec_mask)
        return msg

    def decode_content(self, msg: RawMessage) -> bool:
        """Decode CREATE response message content.

        Returns:
            result : True if successful
        """
        if self._ak:
            # CREATE response - normal flow
            self._omci_result, self._attr_exec_mask = struct.unpack_from("!BH", msg, self.content_offset)
            logger.debug('Decoded OMCI result: {} attr_exec_mask: {} at offset: {}'.format(self._omci_result, self._attr_exec_mask, self.content_offset))
            ret = True
        else:
            # CREATE request - mainly for debugging
            ret = self.decode_attributes(msg, self.content_offset, self._me.attr_mask(access='C'))
        return ret

    def commit(self, onu: 'OnuDriver'):
        """ Commit action results top ONU MIB.

        Args:
            onu : OnuDriver containing the current ONU MIB

        Raises: an exception in case of commit failure
        """
        if not onu.add(self._me):
            raise Exception('{} - failed to commit to the local MIB'.format(self.name))

    def rollback(self, onu: 'OnuDriver') -> 'OmciAction':
        """ Create a roll-back action.

        Args:
            onu : OnuDriver containing the current ONU MIB
        Returns:
            An action that rolls-back 'this' action, or None if not applicable
        """
        # If action failed - there is nothing to rollback
        if self._omci_result != 0:
            return None
        return DeleteAction(self._owner, self._me, self._extended)

    @property
    def is_configuration(self):
        """ Returns: TRUE for configuration handlers that affect mib_sync """
        return True
