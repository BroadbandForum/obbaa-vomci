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
# omci_action_get_all_alarms_next.py : "GET_ALL_ALARMS_NEXT" OMCI action encoder/decoder
#

"""GET_ALL_ALARMS_NEXT action"""
from math import floor
from omci_types import *
from database.omci_me import ME
from database.omci_me_types import MeClassMapper, omci_msg_type, onu_data_me
from mapper.get_yang_response import get_all_alarms_state
import nbi.grpc.service_definition.tr451_vomci_nbi_message_pb2 as tr451_vomci_nbi_message_pb2

import struct
import datetime
from encode_decode.omci_action import OmciAction
from omci_logger import OmciLogger

logger = OmciLogger.getLogger(__name__)

class GetAllAlarmsNextAction(OmciAction):
    """ GetAllAlarmsNextAction: Get All Alarms Next control block
    When OMCI request-response transaction is completed, the message block.

    contains the following attributes:
       me
        num_of_upload_next: number of subsequent MIB upload next commands
    """
    name = 'GET_ALL_ALARMS_NEXT'
    action = omci_msg_type[name]

    def __init__(self, owner: 'OmhHandler' = None):
        """
        Args:
            owner: request owner
            sequence_number: command sequence number
        """
        me = onu_data_me(0)
        super().__init__(self.action, me, True, False, False, owner)

        self._sequence_number = 0
        self._search_ent_cls = None

    def encode_content(self) -> RawMessage:
        """Encode GET_ALL_ALARMS_NEXT request message content.

        Returns:
            raw OMCI message content
        """
        if not self._ak:
            # GET_ALL_ALARMS_NEXT request 
            msg = struct.pack("!H", self._sequence_number)
            self._sequence_number += 1
        else:
            # GET_ALL_ALARMS_NEXT response 
            bitmap = bytearray(28)
            for byte_idx in range(floor(len(self._search_ent_cls.alarms)/8)):
                byte = 0
                for bit_idx in range(8):
                    state = int(self._search_ent_cls.alarms[byte_idx+bit_idx].get_state())
                    byte |=  state << (7 - bit_idx)
                bitmap.extend(byte.to_bytes(1,'little'))
            msg = struct.pack("!HH28s",self._search_ent_cls.me_class, self._search_ent_cls.me_inst,bytes(bitmap))
        return msg

    def decode_content(self, msg: RawMessage) -> bool:
        """Decode GET_ALL_ALARMS message content.

        Returns:
            message content
        """
        if self._ak:
            # GET_ALL_ALARMS_NEXT response 
            me_class_reported_alarm, me_inst_reported_alarm, me_bitmap = struct.unpack_from("!HH28s", msg, self.content_offset)
            me_class_with_alarm = MeClassMapper.me_by_class(me_class_reported_alarm)
            
            if me_class_with_alarm is None:
                #Certificate that exist the class with the specific alarm
                logger.debug("can't decode message for me_class {}".format(me_class_reported_alarm))
                self._search_ent_cls = None
                return False
            
            self._search_ent_cls = me_class_with_alarm(me_inst_reported_alarm)

            for idx in range(len(self._search_ent_cls.alarms)):
                byte = me_bitmap[floor(idx/8)]
                state = bool(byte & (0x80 >> idx))
                self._search_ent_cls.alarms[idx].set_state(state)
 
            logger.debug("decode: {}{}".format(self._search_ent_cls, self._search_ent_cls.alarms and ': OK' or ': FAILED'))   


        else:
            # GET_ALL_ALARMS_NEXT request
            self._sequence_number = struct.unpack_from("!H", msg, self.content_offset)[0]

        return True 