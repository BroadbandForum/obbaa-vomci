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
# omci_olt.py : OLT database
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

"""This module implements per-OLT and multi-OLT databases
"""

from omci_types import *
from omh_nbi.onu_driver import OnuDriver
import threading

class Olt:
    """ Per OLT collectyion of ONUs """

    def __init__(self, id : OltId, channel: 'OltCommChannel'):
        """ Olt Class Constructor.

            Olt is a collection of OnuDriver instances + reference to OmciChannel
            providing a communication path to the pOLT.

        Args:
            id: OLT Id
            channel: Communication channel
        """
        self._id = id
        self._channel = channel
        self._onus = {}
        self._onus_by_name = {}
        self._lock = threading.Lock()

    @property
    def id(self) -> OltId:
        return self._id

    @property
    def channel(self):
        """ The current communication channel with pOLT. None of not connected """
        return self._channel

    def set_channel(self, channel: 'OltCommChannel'):
        """ Set communication channel with pOLT.

        Args:
            channel
        """
        with self._lock:
            self._channel = channel

    def OnuAdd(self, onu_name: OnuName, onu_id: OnuSbiId, tci: int = 0) -> OnuDriver:
        """ Add ONU to the OLT database.

        Args:
            onu_id: ONU Id
            tci: initial TCI value (mainly for debugging)
        Returns:
             ONU driver or None if already exists
        """
        with self._lock:
            if onu_id in self._onus:
                logger.error("OnuAdd: ONU {} is already in the database" % onu_id)
                return None
            onu = OnuDriver(onu_name, onu_id, self, tci)
            self._onus[onu_id] = onu
            self._onus_by_name[onu_name] = onu
        return onu

    def OnuDelete(self, onu_name: OnuName):
        """ Delete ONU from the database.

        Args:
            onu_name: ONU Name
        """
        with self._lock:
            if onu_name not in self._onus_by_name:
                logger.error("OnuDelete: ONU {} is not in the database" % onu_name)
                return
            onu = self._onus_by_name[onu_name]
            del self._onus_by_name[onu_name]
            del self._onus[onu.onu_id]

    def OnuGet(self, onu_id: OnuSbiId, log_error: bool = True) -> OnuDriver:
        """ Get ONU by ID.

        Args:
            onu_id: ONU Id
            log_error: True=error log if ONU is not found
        Returns:
             ONU driver or None if not found
        """
        with self._lock:
            if onu_id not in self._onus:
                if log_error:
                    logger.error("OnuGet: ONU {} is not in the database" % onu_id)
                return None
            return self._onus[onu_id]

    def OnuGetByName(self, onu_name: OnuName, log_error: bool = True) -> OnuDriver:
        """ Get ONU by ID.

        Args:
            onu_name: ONU Name
            log_error: True=error log if ONU is not found
        Returns:
             ONU driver or None if not found
        """
        with self._lock:
            if onu_name not in self._onus_by_name:
                if log_error:
                    logger.error("OnuGet: ONU {} is not in the database" % onu_name)
                return None
            return self._onus_by_name[onu_name]

    def send(self, onu: OnuDriver, msg: RawMessage) -> bool:
        """ Send raw OMCI message to ONU.

        Args:
            onu: ONU object
            msg: raw OMCI message without CRC/MIC
        """
        with self._lock:
            if not self._channel:
                logger.error("send: can't send message to ONU {}. No active channel".format(onu.onu_id))
                return False
            return self._channel.send(onu, msg)

    def recv(self, onu_id: OnuSbiId, msg: RawMessage):
        """ Receive an OMCI message.

            This function is called by an OmciChannel service when a new OMCI message is received from pOLT.<br>
            The function forwards the message to the relevant OnuDriver.

        Args:
            onu_id: ONU Id
            msg: raw OMCI message without CRC/MIC
        """
        with self._lock:
            if onu_id not in self._onus:
                logger.error("Received packet for an unknown ONU {}".format(onu_id))
                return
            onu = self._onus[onu_id]
        onu.recv(msg)


class OltDatabase:
    """ OltDatabase is a collection of OLTs """

    _olts = {}
    _lock = threading.Lock()

    @classmethod
    def OltAddUpdate(cls, olt_id: OltId, channel: 'OltCommChannel') -> Olt:
        """ Add OLT to the database or update an existing OLT.

        Args:
            olt_id: OLT Id
            channel: communication channel to pOLT

        Returns:
            Olt object instance
        """
        with cls._lock:
            if olt_id in cls._olts:
                olt = cls._olts[olt_id]
                olt.set_channel(channel)
            else:
                olt = Olt(olt_id, channel)
                cls._olts[olt_id] = olt
        return olt

    @classmethod
    def OltDelete(cls, olt_id: OltId):
        """ Delete OLT from the database.

        Args:
            olt_id: OLT Id
        """
        with cls._lock:
            if olt_id not in cls._olts:
                logger.error("OltDelete: OLT {} is not in the database" % olt_id)
                return
            del cls._olts[olt_id]

    @classmethod
    def OltGet(cls, olt_id: OltId) -> Olt:
        """ Find OLT by id.

        Args:
            olt_id: OLT Id
        """
        with cls._lock:
            if olt_id not in cls._olts:
                return None
            return cls._olts[olt_id]
