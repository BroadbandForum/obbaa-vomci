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
# ONU driver. Implements the committed and the pending ONU MIBs,
# request-response correlation and timeout
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

"""This module implements ONU driver class that includes ONU MIB
and additional functions and properties for request-response correlation.
"""
from typing import Tuple, Dict
from omci_types import OnuSbiId, RawMessage, OnuName
from database.omci_me_types import omci_me_class
from database.omci_me import ME
from database.omci_onu_mib import OnuMib
from encode_decode.omci_action import OmciAction
from omci_logger import OmciLogger
import threading

logger = OmciLogger.getLogger(__name__)

DEFAULT_MAX_RETRIES = 3         # Default number of message retransmissions in case of timeout
DEFAULT_ACK_TIMEOUT = 3.0       # Default ack timeout

class OnuDriver():
    """ Per-ONU driver.
        This object is created by Olt.OnuAdd() factory.
    """

    _message_handler_by_mt = {}

    def __init__(self, onu_name: OnuName, onu_id: OnuSbiId, olt: 'Olt', tci = 0):
        """
        Args:
            onu_id : ONU Id
            olt : OLT this ONU belongs to
            tci : initial TCI value
        """
        assert olt is not None
        super().__init__()
        self._onu_id = onu_id
        self._onu_name = onu_name
        self._pending_requests = [] # Each entry is a tuple [tci, OmhHandler]
        self._tci = (0 <= tci <= 0x7ffff) and tci or 0
        self._olt = olt
        self._lock = threading.Lock()
        self._max_retries = DEFAULT_MAX_RETRIES
        self._ack_timeout = DEFAULT_ACK_TIMEOUT
        self._main_mib = OnuMib(onu_id) # TODO maybe should onu_name instead of onu_id?
        self._candidate_mib = OnuMib(onu_id)

    @property
    def onu_id(self):
        return self._onu_id

    def set_onu_id(self, onu_id: OnuSbiId):
        self._onu_id = onu_id

    @property
    def onu_name(self):
        return self._onu_name

    @classmethod
    def register(cls, message_type : int, handler):
        """ Register unsolicited message handler.

        Args:
            mt: OMCI message type (5 bit action value)
            handler: a callable handler(OnuDriver instance, raw_message)
        """
        OnuDriver._message_handler_by_mt[message_type] = handler

    @property
    def olt(self):
        """ OLT this ONU belongs to """
        return self._olt

    @property
    def next_tci(self) -> int:
        """ This function resturns the next TCI value to be transmitted """
        with self._lock:
            self._tci = (self._tci == 0x7fff) and 1 or self._tci + 1
            tci = self._tci
        return tci

    @property
    def max_retries(self) -> int:
        """ This function returns the max number of retransmissions allowed for this ONU."""
        return self._max_retries

    @property
    def ack_timeout(self) -> float:
        """ Response timeout value (s).

        OMH handler waits for response for ack_timeout (s) before retransmitting
        or reporting a TIMEOUT failure.
        """
        return self._ack_timeout

    def set_flow_control(self, max_retries: int = DEFAULT_MAX_RETRIES, ack_timeout: float = DEFAULT_ACK_TIMEOUT):
        """ Set flow control parameters.

        Args:
            max_retries: max number of retransmissions. Set =0 to disable retransmissions
            ack_timeout: max time waiting for acknowledge (in seconds and fractions of a second)
        """
        self._max_retries = max_retries
        self._ack_timeout = ack_timeout

    def send(self, sender: 'OmhHandler', msg: RawMessage, ar: bool = True, tci : int = 0) -> bool:
        """ Send message to ONU.

        Args:
            sender : request sender OMH handler
            msg : raw OMCI message (without MIC)
            ar : TRUE (default) if acknowledge is required. In this case when Ack is received
                 the driver will notify the 'sender' by calling 'sender->recv(raw_message)'
            tci : TCI for Request/Ack correlation
        Returns:
            TRUE if message was sent successfully
        """
        with self._lock:
            ret = self._olt.send(self, msg)
            if ret and ar:
                self._pending_requests.append((tci, sender))
        return ret

    def remove_pending(self, sender):
        """ Remove pending request(s) by the 'sender'.

        Args:
            sender : request sender, the same as passed to send() method
        """
        with self._lock:
            for _tci, _sender in self._pending_requests:
                if _sender == sender:
                    self._pending_requests.remove((_tci, _sender))

    def recv(self, msg: RawMessage):
        """ Message received from ONU.

        This function is called by communication layer.

        Args:
            msg - Raw OMCI message
        """
        # Peek in the common OMCI message header
        tci, ak, action = OmciAction.decode_key_fields(msg)

        # If this is a response, identify the requester.
        # Otherwise, deliver to the registered subscriber for the action
        if ak:
            sender = None
            with self._lock:
                for _tci, _sender in self._pending_requests:
                    if _tci == tci:
                        self._pending_requests.remove((_tci, _sender))
                        sender = _sender
                        break
            if sender:
                sender.recv(msg)
            else:
                logger.warning("recv: unexpected ACK with TCI {} from ONU {} discarded.".format(tci, self._onu_id))
        else:
            # Not a response. Identify message handler by message type
            if action not in OnuDriver._message_handler_by_mt:
                logger.error("recv: Don't know how to handle MT {} from ONU {}. Message discarded.".format(
                    action, self._onu_id))
                return
            OnuDriver._message_handler_by_mt[action].recv(self, msg)

    #
    # MIB management
    #

    def increment_mib_sync(self):
        """ Increment MIB sync counter """
        onu_data = self._main_mib.get(omci_me_class['ONU_DATA'], 0, False)
        cand_onu_data = self._candidate_mib.get(omci_me_class['ONU_DATA'], 0, False)
        if onu_data is None and cand_onu_data is None:
            logger.error("Can't increment mib_sync. onu_data ME doesn't exist in the local MIB")
            return
        if onu_data is not None:
            onu_data.mib_data_sync = 1 if onu_data.mib_data_sync >= 255 else onu_data.mib_data_sync + 1
            if cand_onu_data is not None:
                cand_onu_data.mib_data_sync = onu_data.mib_data_sync
        else:
            cand_onu_data.mib_data_sync = 1 if cand_onu_data.mib_data_sync >= 255 else cand_onu_data.mib_data_sync + 1

    def clear_candidate(self):
        """ Clear candidate MIB """
        self._candidate_mib.clear()

    def clear(self):
        """ Clear the candidate MIB and the main MIB """
        self._main_mib.clear()
        self.clear_candidate()

    def commit(self, me_class : int = None ):
        """ Commit candidate MIB into the main MIB """
        self._main_mib.merge(self._candidate_mib, me_class)
        self.clear_candidate()

    def add(self, me: ME) -> bool:
        """Add ME to the database

        Args:
            me: ME object
        Returns:
            True if successful, False if [me_class, me_inst] already exists in the MIB
        """
        return self._candidate_mib.add(me)

    def set(self, me: ME) -> bool:
        """Update an existing ME in the candidate database.
           The values in me stored in the MIB are merged with values passed in parameters

        Args:
            me: ME object
        Returns:
            True if successful, False if [me_class, me_inst] doesn't exists in the MIB
        """
        ret = self._candidate_mib.set(me, False)
        if not ret:
            # Not in the candidate yet. add it
            ret = self._candidate_mib.add(me)
        return ret

    def get(self, me_class: int, inst: int, log_error: bool = True, clone: bool = False) -> ME:
        """Get ME from the database. Look in the candidate first, then in the main MIB

        Args:
            me_class: ME object class
            inst: ME object instance
            clone: True-return a deep copy of the ME stored in the MIB,
                   False-return the original ME
        Returns:
            ME if successful, None if [me_class, me_inst] doesn't exist in the MIB
        """
        me = self._candidate_mib.get(me_class, inst, False, False)
        if me is None:
            me = self._main_mib.get(me_class, inst, log_error, clone)
            if me is not None and clone:
                self._candidate_mib.add(me)
        return me

    def get_by_name(self, name: str, clone: bool = False) -> ME:
        """ Get ME by name. Look in the candidate first, then in the main MIB

        Args:
            name: name associated with an ME using me.user_name
            clone: True-return a deep copy of the ME stored in the MIB,
                   False-return the original ME
        Returns:
            ME instance or None if not found
        """
        me = self._candidate_mib.get_by_name(name, False)
        if me is None:
            me = self._main_mib.get_by_name(name, clone)
            if me is not None and clone:
                self._candidate_mib.add(me)
        return me

    def get_first(self, me_class: int) -> ME:
        """Get first ME with specific ME class. Look in the candidate MIB first, then the main MIB

        Args:
            me_class: ME object class
        Returns:
            ME if successful, None if there are no instances of me_class
        """
        me = self._candidate_mib.get_first(me_class)
        if me is None:
            me = self._main_mib.get_first(me_class)
        return me


    def get_all_instance_ids(self, me_class: int) -> Tuple[int, ...]:
        """Get tuple including all instance ids of the specified me_class

        Args:
            me_class: ME object class
        Returns:
            tuple of all instance ids of the specified me_class
        """
        cand_list = self._candidate_mib.get_all_instance_ids(me_class)
        main_list = self._main_mib.get_all_instance_ids(me_class)
        return tuple(sorted(dict.fromkeys(cand_list + main_list)))

    @staticmethod
    def _me_inst(me: ME):
        return me.inst

    def get_all_instances(self, me_class: int) -> Tuple[ME, ...]:
        """Get tuple including all MEs of the specified ma_class

        Args:
            me_class: ME object class
        Returns:
            tuple of all MEs of the specified me_class
        """
        cand_list = self._candidate_mib.get_all_instances(me_class)
        main_list = self._main_mib.get_all_instances(me_class)
        return tuple(sorted(dict.fromkeys(cand_list + main_list), key=OnuDriver._me_inst))

    def get_all_me_classes(self) -> Tuple[int,...]:
        """Get tuple including all ME classes

           Returns:
               tuple of all ME classes
        """
        cand_list = self._candidate_mib.get_all_me_classes()
        main_list = self._main_mib.get_all_me_classes()
        return tuple(sorted(dict.fromkeys(cand_list + main_list)))

    def dump_mib(self):
        """Dump the main MIB to the screen"""
        print('=== Start of MIB dump for ONU {} ==='.format(self._onu_id))
        all_me_classes = self.get_all_me_classes()
        for me_class in all_me_classes:
            for me in self.get_all_instances(me_class):
                print('{}'.format(me))
        print('=== End of MIB dump for ONU {} ==='.format(self._onu_id))

