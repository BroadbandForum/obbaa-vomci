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
# omci_action_mib_upload_next.py : "MIB_UPLOAD_NEXT" OMCI action encoder/decoder
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

"""MIB_UPLOAD_NEXT action"""
from omci_types import *
from database.omci_me import ME
from database.omci_me_types import omci_msg_type, onu_data_me, MeClassMapper
from encode_decode.omci_action import OmciAction
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class MibUploadNextAction(OmciAction):
    """ MibUploadNext: MIB_UPLOAD_NEXT control block.

    When OMCI request-response transaction is completed, the message block
    contains the following attributes:
        me - ONU data
        upload_me - Uploaded ME
    """

    name = 'MIB_UPLOAD_NEXT'
    action = omci_msg_type[name]

    def __init__(self, owner: 'OmhHandler'):
        """
        Args:
            owner: request owner
            sequence_num: command sequence number
        """
        me = onu_data_me(0)
        super().__init__(self.action, me, True, False, False, owner)
        self._sequence_num = 0
        self._upload_me = None
        self._prev_remaining_attr_mask = 0

    def attr_mask_no_tables(self) -> int:
        attr_mask = self._upload_me.attr_mask()
        for a in self._upload_me.attrs:
            if a.is_table:
                attr_mask &= ~a.mask
        return attr_mask

    def encode_content(self) -> RawMessage:
        """Encode MIB_UPLOAD_NEXT message content.

        Returns:
            raw OMCI message content
        """
        if not self._ak:
            # MIB_UPLOAD_NEXT request - normal flow
            msg = struct.pack("!H", self._sequence_num)
            self._sequence_num += 1
        else:
            # MIB_UPLOAD_NEXT response - mainly for debugging. self.upload_me must be set
            if not self._upload_me:
                logger.error("mib_upload_next:encode: can't encode response without self.upload_me")
                return bytearray()

            if self._prev_remaining_attr_mask == 0:
                self._prev_remaining_attr_mask = self.attr_mask_no_tables()
            self.set_attr_mask(self._prev_remaining_attr_mask)
            # attr_mask will be updated below
            msg = struct.pack("!HHH", self._upload_me.me_class, self._upload_me.inst, 0)
            msg += self.encode_attributes(msg, encode_me = self._upload_me)
            attr_mask = self._prev_remaining_attr_mask & ~self.remaining_attr_mask
            struct.pack_into("!H", msg, 4, attr_mask)
            self._prev_remaining_attr_mask = self.remaining_attr_mask
        return msg

    def decode_content(self, msg: RawMessage) -> bool:
        """Decode MIB_UPLOAD response message content.

        Returns:
            result : True if successful
        """
        if self._ak:
            # MIB_UPLOAD_NEXT response - normal flow
            me_class, inst, attr_mask = struct.unpack_from("!HHH", msg, self.content_offset)
            # Create & populate upload_me
            me_class_type = MeClassMapper.me_by_class(me_class)
            if me_class_type is None:
                # This is not an error. There are many ME classes that we don't support
                logger.debug("can't decode message for me_class {}. Skipped".format(me_class))
                self._upload_me = None
                return True
            # Decode attributes
            self._upload_me = me_class_type(inst)
            ret = self.decode_attributes(msg, self.content_offset + 6, attr_mask, decode_me=self._upload_me)
            logger.debug("decode: {}{}".format(self._upload_me, ret and ': OK' or ': FAILED'))
        else:
            # MIB_UPLOAD_NEXT request - debug flow
            self._sequence_num = struct.unpack_from("!H", msg, self.content_offset)[0]
        return ret
