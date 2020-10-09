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
# omci_action.py : Base class for all OMCI actions
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

"""OMCI Action encoding/decoding"""
from typing import Tuple
from omci_types import *
from database.omci_me import ME
from database.omci_me_types import MeClassMapper
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class OmciAction(AutoGetter):
    """Helper class for OMCI message encode/decode"""
    _action_class_by_mt = {}

    def __init__(self, action: int, me : ME = None, ar: bool = True, ak: bool = False, extended : bool = False,
                 owner: 'OmhHandler' = None):

        self._action = action
        self._ar = ar
        self._ak = ak
        self._extended = extended
        self._me = me
        self._tci = 0
        self._attr_mask = 0
        self._remaining_attr_mask = 0
        self._content_len = 0
        self._total_len = 0
        self._content_offset = extended and 10 or 8
        self._owner = owner
        self._me_class = me and me.me_class or 0xffff
        self._inst = me and me.inst or 0xffff
        self._tci = 0
        self._metadata = {}
        self._content_len = 0  # will be calculated for extended
        self._total_len = self._extended and 2044 or 44  # XXX max extended length should be configurable
        self._omci_result = 0

    def set_length(self, content_len: int, total_len: int, content_offset: int):
        self._content_len = content_len
        self._total_len = total_len

    def set_header_fields(self, tci: int, ar: bool, ak: bool, me_class: int, inst: int):
        self._tci = tci
        self._ar = ar
        self._ak = ak
        self._me_class = me_class
        self._inst = inst

    def reinit(self):
        """ Re-initialize action, prepare for reuse """
        self._ar = self._ar or self._ak
        self._ak = False
        self._content_len = 0  # will be calculated for extended
        self._total_len = self._extended and 2044 or 44  # XXX max extended length should be configurable

    @property
    def is_configuration(self):
        """ Return TRUE for configuration handlers that affect mib_sync """
        return False

    # Basic sanity
    def validate(self, msg: RawMessage) -> bool:
        if self._content_offset + self._content_len != len(msg):
            logger.error("validate rx: message is insane: content_offset {} content_length {} total_length {}".
                         format(self._content_offset, self._content_len, len(msg)))
            return False
        return True

    def rollback(self, onu: 'OnuDriver') -> 'OmciAction':
        """ Create a roll-back action
        Args:
            onu : OnuDriver containing the current ONU MIB
        Returns:
            An action that rolls-back 'this' action, or None if not applicable
        """
        return None

    def commit(self, onu: 'OnuDriver'):
        """ Commit action results top ONU MIB
        Args:
            onu : OnuDriver containing the current ONU MIB
        Raises an exception in case of commit failure
        """
        pass

    def set_attr_mask(self, attr_mask: int):
        self._attr_mask = attr_mask
        self._remaining_attr_mask = attr_mask

    def encode_common_hdr(self, tci: int) -> RawMessage:
        assert self._me is not None
        self._tci = tci
        mt = (int(self._ar)<<6) | (int(self._ak)<<5) | self._action
        if self._extended:
            msg = struct.pack('!HBBHHH', self._tci, mt, 0x0b, self._me.number, self._me.inst, self._content_len)
        else:
            msg = struct.pack('!HBBHH', self._tci, mt, 0x0a, self._me.number, self._me.inst)
        return msg

    def encode_attributes(self, msg : RawMessage, encode_values: bool = True,
                          table_length : bool = False, encode_me : ME = None) -> RawMessage:
        # Pack content
        encode_me = (encode_me is None) and self._me
        content = bytearray()
        max_content_len = self._total_len - len(msg)
        mask = self._remaining_attr_mask
        idx = 15
        while mask != 0:
            while mask & (1 << idx) == 0:
                idx -= 1
            attr_idx = 16 - idx # attribute mask counts from MSB
            attr = encode_me.attr(attr_idx)

            # For some requests table attribute size must be encoded as 4 byte number instead of the actual table data.
            # XXX table support needs to be added. For now just encode table record size
            size = (table_length and attr.is_table) and 4 or attr.size
            if size > max_content_len:
                break
            max_content_len -= size
            if encode_values:
                if table_length and attr.is_table:
                    value = (attr.name in self._metadata) and self._metadata[attr.name] or attr.size
                    content += NumberDatum(4).encode(value)
                else:
                    content += encode_me.attr_encode(attr_idx)
            mask &= ~(1 << idx)

        self._content_len = len(content)
        self._remaining_attr_mask = mask
        return content

    def encode_content_len(self, msg : RawMessage) -> RawMessage:
        cl = bytearray(2)
        struct.pack_into('!H', cl, self._content_len)
        msg[8:10] = cl
        return msg

    def pad(self, msg : RawMessage) -> RawMessage:
        if not self._extended and len(msg) < self._total_len:
            msg += bytes(b'\x00' * (self._total_len - len(msg)))
        return msg

    @classmethod
    def register(cls):
        OmciAction._action_class_by_mt[cls.action] = cls

    def decode_attributes(self, msg: RawMessage, offset : int, attr_mask: int,
                          table_length : bool = False, decode_me : ME = None) -> bool:
        """Decode message attributes"""
        decode_me = decode_me is None and self._me or decode_me
        len = self._content_len
        mask = attr_mask
        max_attr_idx = decode_me.num_attrs - 1
        idx = 15
        while mask != 0:
            while mask & (1 << idx) == 0:
                idx -= 1
            attr_idx = 16 - idx  # attribute mask counts from MSB

            if attr_idx > max_attr_idx:
                logger.warning("decode_attributes: invalid attr bit {} in the mask for {}".format(attr_idx, decode_me.name))
                return False

            # Table attributes are skipped for GET requests. 4-byte table attribute length is returned instead
            # It is stored in metadata dict {attr_name: value}
            attr = decode_me.attr(attr_idx)
            size = (attr.is_table and table_length) and 4 or attr.size

            if size > len:
                logger.warning("decode_attributes: message is too short. Can't decode attribute {}".format(attr.name))
                return False

            try:
                if attr.is_table and table_length:
                    value, offset = NumberDatum(4).decode(msg, offset)
                    self._metadata[attr.name] = value
                else:
                    value, offset = attr.data_type.decode(msg, offset)
                    decode_me.set_attr_value(attr_idx, value, True)
            except:
                logger.warning("decode_attributes: error when decoding {}.{} value {}".format(
                    decode_me.name, attr.name, msg[offset:offset+size]))
                return False

            len -= size
            mask &= ~(1 << idx)

        self._remaining_attr_mask &= ~attr_mask

        return True

    @staticmethod
    def decode_key_fields(msg: RawMessage) -> Tuple[int, int, int]:
        """Decode key fields of the raw message
        Args:
            msg: raw OMCI message
        Returns:
            tci, ak, action
        """
        tci, mt, dev = struct.unpack_from('!HBB', msg, 0)
        ak = bool((mt >> 5) & 0x1)
        action = mt & 0x1f
        extended = (dev == 0x0b)
        content_offset = extended and 10 or 8
        content_length = extended and struct.unpack_from('!H', msg, 8)[0] or 36
        return tci, ak, action

    def encode(self, tci: int) -> RawMessage:
        """Encode raw OMCI message
        Args:
            tci: TCID to encode
        Returns:
            Raw OMCI message
        """
        msg = self.encode_common_hdr(tci)
        msg += self.encode_content()
        logger.debug("encode: {} AR={} AK={} TCI={}: {}".format(
            self.name, self._ar, self._ak, tci,
            self._me.to_string(assigned_only=True, attr_mask=self._attr_mask)))
        # As an optimization only log a raw message if at debug level
        if logger.level <= logging.DEBUG:
            logger.debug("encode: ({})-{}".format(len(msg), ''.join(format(x, '02x') for x in msg)))
        return self.pad(msg)

    @staticmethod
    def decode(msg: RawMessage, action_msg: 'OmciAction' = None) -> 'OmciAction':
        """Decode raw OMCI message
        Args:
            msg: raw OMCI message
        Returns:
            OmciAction control block or None in case of error
        """
        if len(msg) < 10:
            logger.error("decode: raw message is too short")
            return None

        # As an optimization only log a raw message if at debug level
        if logger.level <= logging.DEBUG:
            logger.debug("decode: ({})-{}".format(len(msg), ''.join(format(x, '02x') for x in msg)))

        tci, mt, dev, me_class, inst = struct.unpack_from('!HBBHH', msg, 0)
        ar = bool((mt >> 6) & 0x1)
        ak = bool((mt >> 5) & 0x1)
        action = mt & 0x1f
        extended = (dev == 0x0b)

        # OmciAction object usually is already identified when decoding a reply
        # in this case it is passed in parameters, no need to create it here
        if action_msg is None:
            if action not in OmciAction._action_class_by_mt:
                logger.warning("decode: can't decode message with mt {} ak {}".format(mt, ak))
                return None
            cls = OmciAction._action_class_by_mt[action]
            me_class_type = MeClassMapper.me_by_class(me_class)
            if me_class_type is None:
                logger.warning("decode: can't decode message for me_class {}".format(me_class))
                return None

            me = me_class_type(inst)
            action_msg = cls(tci, me=me)
        else: # Existing OmciAction & ME. Make sure that me_class and instance are as expected
            me = action_msg.me
            assert me is not None
            if me.me_class != me_class or me.inst != inst:
                logger.warning("decode: unexpected me_class {}, inst {}. Expected {}, {}".format(
                    me_class, inst, me.me_class, me.inst))
                return None

        action_msg.set_header_fields(tci, ar, ak, me_class, inst)
        if extended:
            action_msg.set_length(struct.unpack_from('!H', msg, 8)[0], len(msg), 10)
        else:
            action_msg.set_length(len(msg) - 8, len(msg), 8)
        if not action_msg.validate(msg):
            return None
        if not action_msg.decode_content(msg):
            return None
        logger.debug("decode: {} AR={} AK={} TCI={}: {}".format(action_msg.name, ar, ak, tci, me))
        return action_msg

    def decode_content(self, msg: RawMessage, content_offset: int) -> bool:
        """Decode message content"""
        raise Exception('Unimplemented decode_content() method')

    def encode_content(self) -> RawMessage:
        """Decode message content"""
        raise Exception('Unimplemented encode_content() method')
