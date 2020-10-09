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
# omci_channel.py : transport type-independent base OMCI channel base class
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" OMCI Communication channel """
from omci_types import *
from omci_logger import OmciLogger
from database.omci_olt import OltDatabase
from typing import Dict

logger = OmciLogger.getLogger(__name__)


# pOLT communication channel
class OltCommChannel(Name):

    def __init__(self, name: str, description: str = ''):
        super().__init__(name, description)
        self._olt = None

    def connect(self, host: str, port: int, auth: Optional['Dict'] = None) -> 'Olt':
        """ Connect with pOlt (client mode))

        The function must be implemented in derived classes.

        Args:
            host: host to connect to
            port: port to connect to
            auth: authentication parameters (TBD)
        Returns:
            'Olt' object it is connected to or None if failed
        """
        raise Exception('Unimplemented connect() method')

    def disconnect(self):
        """ Disconnect from the peer pOlt
        """
        raise Exception('Unimplemented disconnect() method')

    def send(self, onu: 'OnuDriver', msg: RawMessage) -> bool:
        """ Send message to ONU
        The function must be implemented in derived classes.

        Args:
            onu: ONU object
            msg: raw OMCI message without MIC
        Returns:
            True if successful
        """
        raise Exception('Unimplemented send() method')

    def connected(self, olt_id: OltId) -> 'Olt':
        """ Connected indication
        This function is called by the derived class after successful
        completion of Hello exchange.

        Args:
            olt_id: OLT Id reported by the peer pOLT
        Returns:
            Olt object
        """
        logger.info("vOMCI {} is connected to pOLT {}".format(self._name, olt_id))
        self._olt = OltDatabase().OltAddUpdate(olt_id, self)
        return self._olt

    def disconnected(self):
        """ Disconnected indication

        This function is called by the derived class when connection with
        pOLT is broken.
        """
        if self._olt is not None:
            logger.info("vOMCI {} disconnected from pOLT {}".format(self._name, self._olt.id))
            self._olt.set_channel(None)
            OltDatabase().OltDelete(self._olt.id)
            self._olt = None
