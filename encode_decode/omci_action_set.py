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
# omci_action_set.py : "SET" OMCI action encoder/decoder
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

"""SET action"""
from omci_types import *
from database.omci_me import ME
from database.omci_me_types import omci_msg_type, omci_status
from encode_decode.omci_action import OmciAction
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class SetAction(OmciAction):
    """ SetAction: SET control block.

    When OMCI request-response transaction is completed, the message block
    contains the following attributes:
        me
        omci_result: 0=good, otherwise bad (see omci_result_code Enum)
        opt_attr_mask: Optional-attribute mask: 1 for unsupported optional attributes.
                     contains a valid value only if omci_result=9
        attr_exec_mask: Attribute execution mask: 1 for every failed attribute.
                     contains a valid value only if omci_result=9
    """
    name = 'SET'
    action = omci_msg_type[name]

    def __init__(self, owner: 'OmhHandler', me: ME, attr_names: Optional[Tuple[str, ...]] = None,
                 extended : bool = False):
        """
        Args:
            owner: request owner
            me: ME to be sent
            extended: pass True to generate an extended OMCI message
        """
        assert self.name.lower() in me.actions
        super().__init__(self.action, me, True, False, extended, owner)
        if attr_names is None or logger.level <= logging.DEBUG:
            assigned_attr_numbers = me.attr_numbers(assigned_only=True)
        if attr_names is None:
            attr_names = assigned_attr_numbers
        mask = 0
        for an in attr_names:
            mask |= me.attr(an).mask

        # Check that all assigned attributes are being set.
        # It adds an overhead, so, do it only when in debug mode
        if logger.level <= logging.DEBUG and attr_names is not assigned_attr_numbers:
            for an in assigned_attr_numbers:
                if (me.attr(an).mask & mask) == 0 and not me.attr_is_encoded(an):
                    logger.warning("Attribute {} is assigned but is not going to be set".format(me.attr(an).name))

        self.set_attr_mask(mask)
        self._opt_attrs_mask = 0
        self._attr_exec_mask = 0

    def encode_content(self) -> RawMessage:
        """Encode SET request message content.

        Returns:
            raw OMCI message content
        """
        if not self._ak:
            # SET request - normal flow
            msg = struct.pack("!H", self._attr_mask)
            msg += self.encode_attributes(msg)
        else:
            # SET response - mainly for debugging
            msg = struct.pack("!HHH", self._omci_result, self._opt_attrs_mask, self._attr_exec_mask)
        return msg

    def decode_content(self, msg: RawMessage) -> bool:
        """Decode SET message content.

        Returns:
            result : True if successful
        """
        if self._ak:
            # SET response - normal flow
            self._omci_result, self._opt_attrs_mask, self._attr_exec_mask = struct.unpack_from(
                "!BHH", msg, self.content_offset)
            logger.debug('Decoded OMCI result: {} att_mask: {} att_exec_mask: {} at offset: {}'.format(self._omci_result, self._opt_attrs_mask, self._attr_exec_mask, self.content_offset))
            ret = True
        else:
            # SET request - mainly for debugging
            self._attr_mask = struct.unpack_from("!H", msg, self.content_offset)[0]
            ret = self.decode_attributes(msg, self.content_offset + 2, self._attr_mask)
        return ret

    def commit(self, onu: 'OnuDriver'):
        """ Commit action results top ONU MIB.

        Args:
            onu : OnuDriver containing the current ONU MIB
        Raises: an exception in case of commit failure
        """
        if not onu.set(self._me):
            raise Exception('{} - failed to commit to the local MIB'.format(self.name))

    def rollback(self, onu: 'OnuDriver') -> 'OmciAction':
        """ Create a roll-back action.

        Args:
            onu : OnuDriver containing the current ONU MIB
        Returns:
            An action that rolls-back 'this' action, or None if not applicable
        """
        # If action failed - there is nothing to rollback
        if self._omci_result != 0 and self._omci_result != omci_status['ATTRIBUTES_FAILED_OR_UNKNOWN']:
            return None
        # Lookup ME in the ONU MIB. It is OK if it fails. It might've been set after CREATE.
        # In this case the CREATE's rollback will take care of it
        old_me = onu.get(self._me_class, self._inst, log_error = False)
        if old_me is None:
            return None
        return SetAction(self._owner, old_me, extended=self._extended)

    @property
    def is_configuration(self):
        """ Returns: TRUE for configuration handlers that affect mib_sync """
        return True

