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

"""This module implements per-OLT and multi-OLT databases
"""

from collections import OrderedDict
from omci_types import *
from omh_nbi.onu_driver import OnuDriver
from omcc.omci_channel import OltCommChannel
import threading


class ManagedOnu:

    def __init__(self, onu_name):
        self._lock = threading.Lock()
        self.onu_name = onu_name
        self.ct_ref = None
        self.olt_name = None
        self.upstream_endpoint_name = None
        self.downstream_endpoint_name = None
        self.onu_id = None
        self.communication_available = False
        self.is_configured = False
        self.voltmf_name = None
        self._channel = None

    def SetCommunication(self, olt_name: str, channel_termination: str,
                         onu_tc_id: int, available: bool,
                         downstream_endpoint_name: str,
                         upstream_endpoint_name: str, voltmf_name: str):
        with self._lock:
            self.is_configured = True
            self.olt_name = olt_name
            self.onu_id = onu_tc_id
            self.ct_ref = channel_termination
            self.communication_available = available
            self.downstream_endpoint_name = downstream_endpoint_name
            self.upstream_endpoint_name = upstream_endpoint_name
            self.voltmf_name = voltmf_name

    def SetDsChannel(self, channel: OltCommChannel):
        self._channel = channel

    def IsConfigured(self):
        return self.is_configured

    def IsConnected(self):
        if not self.communication_available:
            return False
        if self._channel is None:
            return False
        return True

class ManagementChain:
    """ OltDatabase is a collection of OLTs """

    _onus = {}
    _lock = threading.Lock()

    @classmethod
    def CreateOnu(cls, onu_name: OnuName):
        """
        Add ONU with onu_name to management chain.
        Args:
            onu_name: unique name of ONU
        """
        with cls._lock:
            if cls._onus.get(onu_name) is None:
                cls._onus[onu_name] = ManagedOnu(onu_name)
        return cls._onus[onu_name]

    @classmethod
    def GetOnu(cls, onu_name):
        return cls._onus.get(onu_name)

    @classmethod
    def SetOnuCommunication(cls, olt_name: OltId, onu_name: OnuName, channel_termination: str,
                            onu_tc_id: int, available: bool, downstream_endpoint_name: str, upstream_endpoint_name: str,
                            voltmf_name: str):
        with cls._lock:
            if cls._onus.get(onu_name) is None:
                cls._onus[onu_name] = ManagedOnu(onu_name)
            managed_onu = cls._onus.get(onu_name)
            managed_onu.SetCommunication(olt_name, channel_termination, onu_tc_id, available, downstream_endpoint_name,
                                         upstream_endpoint_name, voltmf_name)
        return managed_onu

    @classmethod
    def IsOnuConfigured(cls, onu_name: OnuName):
        onu = cls._onus.get(onu_name)
        if onu is None:
            return False
        else:
            return onu.IsConfigured()

    @classmethod
    def IsOnuConnected(cls, onu_name: OnuName):
        onu = cls._onus.get(onu_name)
        if onu is None:
            return False
        else:
            return onu.IsConnected()

    @classmethod
    def GetManagedOnus(cls):
        return cls._onus.values()

    @classmethod
    def DeleteOnu(cls, onu_name: OnuName):
        with cls._lock:
            managed_onu = cls._onus.get(onu_name)
            if managed_onu is None:
                return None
            cls._onus.pop(onu_name)
            return managed_onu
