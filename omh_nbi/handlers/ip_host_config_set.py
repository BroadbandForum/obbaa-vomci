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
# OMH handler that creates an IP_HOST_CONFIG_DATA.
#
# Created by I.Ternovsky (Broadcom) on 17 July 2020
#

""" Update ip_host_config ME (9.4.1).
"""
from database.omci_me_types import *
from encode_decode.omci_action_set import SetAction
from omh_nbi.omh_handler import OmhHandler, OMHStatus
from omci_logger import OmciLogger
import copy
import enum

logger = OmciLogger.getLogger(__name__)

class IpHostConfigSetHandler(OmhHandler):
    """ Set an ip_host_config ME """

    class IpHostOptions(enum.IntFlag):
        """ OP options. Can be used in combination """
        NONE = 0
        DHCP = 1        # Enable DHCP
        PING = 2        # Respond to pings
        TRACEROUTE = 4  # Respond to traceroute
        ENABLE = 8      # Enable IP stack

    def __init__(self, onu: 'OnuDriver', index: int = 0,
                 ip_options : IpHostOptions = IpHostOptions.DHCP.value | IpHostOptions.ENABLE.value,
                 ip_address : int = 0, mask : int = 0, gateway : int = 0,
                 primary_dns: int = 0, secondary_dns: int = 0):
        """ Set a IP Host Config ME

        Args:
            onu: ONU driver
            index: Relative IP_HOST_CONFIG index. 0=first, 1=second, etc.
            ip_address: IP address (if DHCP is not used)
            mask: subnet mask (if DHCP is not used)
            gateway: Default gateway
            primary_dns: Primary DNS address
            secondary_dns: Secondary DNS address
        Returns:
            handler completion status
        """
        super().__init__(name='ip_host_config_set', onu=onu,
                         description=' Set IP_HOST_CONFIG on {}'.format(onu.onu_id))
        self._index = index
        self._ip_options = ip_options
        self._ip_address = ip_address
        self._mask = mask
        self._gateway = gateway
        self._primary_dns = primary_dns
        self._secondary_dns = secondary_dns

    def _get_ip_host_config_by_index(self, index: int) -> ME:
        """ Get IP host config ME by index
            Returns:
                IP_HOST_CONFIG ME or None if not found
        """
        all_ip_host_mes = self._onu.get_all_instances(omci_me_class['IP_HOST_CONFIG_DATA'])
        if all_ip_host_mes is None or index >= len(all_ip_host_mes):
            return None
        return all_ip_host_mes[index]

    def run_to_completion(self) -> OMHStatus:
        logger.info(self.info())

        # Validate parameters and fetch the relevant MEs
        me = self._get_ip_host_config_by_index(self._index)
        if me is None:
            return self.logerr_and_return(OMHStatus.NO_RESOURCES,
                                          "Can't find an IP_HOST_CONFIG ME with index {}.".format(self._index))

        # Create a copy so that MIB remains unchanged until commit
        me = copy.deepcopy(me)
        me.ip_options = self._ip_options
        attrs = ('ip_options',)
        if self._ip_address != 0:
            me.ip_address = self._ip_address
            attrs += ('ip_address',)
        if self._mask != 0:
            me.mask = self._mask
            attrs += ('mask',)
        if self._gateway != 0:
            me.gateway = self._gateway
            attrs += ('gateway',)
        if self._primary_dns != 0:
            me.primary_dns = self._primary_dns
            attrs += ('primary_dns',)
        if self._secondary_dns != 0:
            me.secondary_dns = self._secondary_dns
            attrs += ('_secondary_dns',)
        return self.transaction(SetAction(self, me, attrs))
