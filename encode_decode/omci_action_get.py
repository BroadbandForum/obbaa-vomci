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
# omci_action_get.py : "GET" OMCI action encoder/decoder
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

"""GET action"""
from omci_types import *
from database.omci_me import ME
from database.omci_me_types import omci_msg_type
from encode_decode.omci_action import OmciAction
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class GetAction(OmciAction):
    """ GetAction: GET control block
    When OMCI request-response transaction is completed, the message block.

    contains the following attributes:
        me containing the requested attribute values
        omci_result: 0=good, otherwise bad (see omci_result_code Enum)
        opt_attr_mask: Optional-attribute mask: 1 for unsupported optional attributes.
                     contains a valid value only if omci_result=9
        attr_exec_mask: Attribute execution mask: 1 for every failed attribute.
                     contains a valid value only if omci_result=9
    """
    name = 'GET'
    action = omci_msg_type[name]

    def __init__(self, owner: 'OmhHandler' = None, me: ME = None,
                 attr_names: Optional[Tuple[str, ...]] = None, extended : bool = False):
        """
        Args:
            owner: request owner
            me: ME to be sent
            attr_names: optional list of arguments to be set. If None, all assigned me attributes will be set
            extended: pass True to generate an extended OMCI message
        """
        assert me is not None
        assert self.name.lower() in me.actions
        super().__init__(self.action, me, True, False, extended, owner)
        if attr_names is None:
            attr_names = me.attr_numbers()
        mask = 0
        for an in attr_names:
            mask |= me.attr(an).mask
        self.set_attr_mask(mask)
        self._opt_attrs_mask = 0
        self._attr_exec_mask = 0

    def encode_content(self) -> RawMessage:
        """Encode GET request message content.

        Returns:
            raw OMCI message content
        """
        if not self._ak:
            # GET request - normal flow
            msg = struct.pack("!H", self._attr_mask)
        else:
            # GET response - mainly for debugging
            msg = struct.pack("!HHH", self._omci_result, self._opt_attrs_mask, self._attr_exec_mask)
            self._remaining_attr_mask = self._attr_mask & ~(self._opt_attrs_mask | self._attr_exec_mask)
            msg += self.encode_attributes(self, msg, encode_values=True, table_length=True)
        return msg

    def decode_content(self, msg: RawMessage) -> bool:
        """Decode GET message content.

        Returns:
            result : True if successful
        """
        if self._ak:
            # GET response - normal flow
            self._omci_result, decode_mask = struct.unpack_from("!BH", msg, self.content_offset)
            ret = self.decode_attributes(msg, self.content_offset + 3, decode_mask, table_length=True)
        else:
            # GET request - mainly for debugging
            self._attr_mask = struct.unpack_from("!H", msg, self.content_offset)[0]
            ret = True
        return ret

    def commit(self, onu: 'OnuDriver'):
        """ Commit action results top ONU MIB.

        Args:
            onu : OnuDriver containing the current ONU MIB
        Raises: an exception in case of commit failure
        """
        if not onu.set(self._me):
            raise Exception('{} - failed to commit to the local MIB'.format(self.name))
